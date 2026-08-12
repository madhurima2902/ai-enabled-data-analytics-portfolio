import numpy as np
import pandas as pd
from pathlib import Path

SEED = 2902
rng = np.random.default_rng(SEED)
OUT = Path(__file__).resolve().parents[1] / "data"
OUT.mkdir(parents=True, exist_ok=True)
N_QUOTES, N_POLICIES, N_VEHICLES, N_CLAIMS = 80_000, 32_000, 40_000, 6_500

quote_ids=np.array([f"Q{100000+i}" for i in range(N_QUOTES)],dtype=object)
quotes=pd.DataFrame({"quote_id":quote_ids,"quote_date":pd.to_datetime(rng.choice(pd.date_range("2024-01-01","2025-12-31",freq="D"),N_QUOTES)),"state":rng.choice(["TX","CA","FL","NY","IL","GA","PA","OH","NC","AZ"],N_QUOTES),"channel":rng.choice(["Broker","Direct","Partner"],N_QUOTES,p=[.62,.22,.16]),"segment":rng.choice(["Local Delivery","Contractor","Service Fleet","Long Haul","Specialty"],N_QUOTES),"quoted_premium":np.round(rng.lognormal(np.log(1800),.45,N_QUOTES),2)})
bound_idx=rng.choice(np.arange(N_QUOTES),N_POLICIES,replace=False)
quotes["quote_status"]=rng.choice(["Declined","Expired","Withdrawn"],N_QUOTES,p=[.45,.40,.15]); quotes.loc[bound_idx,"quote_status"]="Bound"
policy_ids=np.array([f"P{200000+i}" for i in range(N_POLICIES)],dtype=object); policy_quote_idx=rng.permutation(bound_idx)
effective_date=quotes.loc[policy_quote_idx,"quote_date"].reset_index(drop=True)+pd.to_timedelta(rng.integers(0,15,N_POLICIES),unit="D")
expiration_date=effective_date+pd.to_timedelta(rng.choice([180,365],N_POLICIES,p=[.12,.88]),unit="D")
written_premium=np.maximum(np.round(quotes.loc[policy_quote_idx,"quoted_premium"].to_numpy()*rng.normal(1,.08,N_POLICIES),2),300)
policies=pd.DataFrame({"policy_id":policy_ids,"quote_id":quotes.loc[policy_quote_idx,"quote_id"].to_numpy(),"effective_date":effective_date,"expiration_date":expiration_date,"written_premium":written_premium,"policy_status":rng.choice(["Active","Expired","Cancelled"],N_POLICIES,p=[.38,.52,.10])})
vehicle_counts=np.ones(N_POLICIES,dtype=int); vehicle_counts[rng.choice(np.arange(N_POLICIES),N_VEHICLES-N_POLICIES,replace=False)]+=1
rows=[]; v=300000
for i,c in enumerate(vehicle_counts):
    for _ in range(c): rows.append([f"V{v}",policy_ids[i],rng.choice(["Ford","Chevrolet","Ram","Freightliner","Isuzu","Hino","GMC"]),rng.choice(["Van","Pickup","Box Truck","Tractor","Flatbed"]),int(rng.integers(2008,2026))]); v+=1
vehicles=pd.DataFrame(rows,columns=["vehicle_id","policy_id","make","vehicle_type","model_year"])
premiums=pd.DataFrame({"premium_id":[f"PR{400000+i}" for i in range(N_POLICIES)],"policy_id":policy_ids,"written_premium":written_premium.copy(),"earned_premium":np.round(written_premium*rng.uniform(.25,1,N_POLICIES),2),"billing_plan":rng.choice(["Monthly","Quarterly","Annual"],N_POLICIES,p=[.52,.18,.30])})
claim_policy_idx=rng.integers(0,N_POLICIES,N_CLAIMS); claim_dates=[]
for i in claim_policy_idx:
    e=pd.Timestamp(effective_date.iloc[i]); x=pd.Timestamp(expiration_date.iloc[i]); claim_dates.append(e+pd.Timedelta(days=int(rng.integers(0,(x-e).days+1))))
paid=np.round(rng.lognormal(np.log(4500),1,N_CLAIMS),2)
claims=pd.DataFrame({"claim_id":[f"C{500000+i}" for i in range(N_CLAIMS)],"policy_id":policy_ids[claim_policy_idx],"claim_date":claim_dates,"claim_status":rng.choice(["Open","Closed"],N_CLAIMS,p=[.23,.77]),"paid_loss":paid,"case_reserve":np.round(paid*rng.uniform(.05,.80,N_CLAIMS),2),"claim_type":rng.choice(["Collision","Liability","Comprehensive","Cargo","Injury"],N_CLAIMS,p=[.32,.30,.18,.08,.12])})

manifest=[]
def log(t,table,i,key): manifest.append({"exception_type":t,"table_name":table,"row_index":int(i),"record_key":str(key)})
non_bound=np.setdiff1d(np.arange(N_QUOTES),bound_idx); targets=rng.choice(non_bound[1000:],180,False); sources=rng.choice(non_bound[:900],180,False)
for i,j in zip(targets,sources): quotes.at[i,"quote_id"]=quotes.at[j,"quote_id"]; log("DUPLICATE_QUOTE_ID","quotes",i,quotes.at[i,"quote_id"])
for i in rng.choice(np.arange(N_POLICIES),140,False): policies.at[i,"quote_id"]=None; log("MISSING_POLICY_QUOTE_KEY","policies",i,policies.at[i,"policy_id"])
for n,i in enumerate(rng.choice(np.arange(N_VEHICLES),190,False)): vehicles.at[i,"policy_id"]=f"P_ORPH_{n:04d}"; log("ORPHAN_VEHICLE_POLICY","vehicles",i,vehicles.at[i,"vehicle_id"])
pm_rows=rng.choice(np.arange(N_POLICIES),175,False)
for i in pm_rows: premiums.at[i,"written_premium"]=round(float(premiums.at[i,"written_premium"]*rng.uniform(1.12,1.35)),2); log("PREMIUM_RECON_MISMATCH","premiums",i,premiums.at[i,"premium_id"])
oc_rows=rng.choice(np.arange(N_CLAIMS),135,False)
for n,i in enumerate(oc_rows): claims.at[i,"policy_id"]=f"P_CLM_ORPH_{n:04d}"; log("ORPHAN_CLAIM_POLICY","claims",i,claims.at[i,"claim_id"])
claim_ps=set(claims.loc[~claims.policy_id.astype(str).str.startswith("P_CLM_ORPH"),"policy_id"]); no_claim=np.array([i for i,p in enumerate(policy_ids) if p not in claim_ps])
for i in rng.choice(no_claim,120,False): policies.at[i,"expiration_date"]=policies.at[i,"effective_date"]-pd.Timedelta(days=int(rng.integers(1,31))); log("INVALID_POLICY_DATE_RANGE","policies",i,policies.at[i,"policy_id"])
valid_claim=np.array([i for i in range(N_CLAIMS) if i not in set(oc_rows)]); pos={p:i for i,p in enumerate(policy_ids)}
for i in rng.choice(valid_claim,110,False): p=claims.at[i,"policy_id"]; claims.at[i,"claim_date"]=pd.Timestamp(expiration_date.iloc[pos[p]])+pd.Timedelta(days=int(rng.integers(10,121))); log("CLAIM_OUTSIDE_POLICY_TERM","claims",i,claims.at[i,"claim_id"])
for i in rng.choice(np.setdiff1d(np.arange(N_POLICIES),pm_rows),80,False): premiums.at[i,"written_premium"]=round(float(-rng.uniform(100,3000)),2); log("NONPOSITIVE_WRITTEN_PREMIUM","premiums",i,premiums.at[i,"premium_id"])
for i in rng.choice(np.arange(N_VEHICLES),70,False): vehicles.at[i,"model_year"]=int(rng.choice([1900,1905,2035,2040])); log("INVALID_VEHICLE_MODEL_YEAR","vehicles",i,vehicles.at[i,"vehicle_id"])

m=pd.DataFrame(manifest); pset=set(policies.policy_id); detected={}
detected["DUPLICATE_QUOTE_ID"]=int(quotes.duplicated("quote_id",keep="first").sum()); detected["MISSING_POLICY_QUOTE_KEY"]=int(policies.quote_id.isna().sum()); detected["ORPHAN_VEHICLE_POLICY"]=int((~vehicles.policy_id.isin(pset)).sum())
r=premiums.merge(policies[["policy_id","written_premium"]],on="policy_id",suffixes=("_premium","_policy")); detected["PREMIUM_RECON_MISMATCH"]=int(((r.written_premium_premium>0)&((r.written_premium_premium-r.written_premium_policy).abs()>.01)).sum()); detected["ORPHAN_CLAIM_POLICY"]=int((~claims.policy_id.isin(pset)).sum()); detected["INVALID_POLICY_DATE_RANGE"]=int((policies.expiration_date<policies.effective_date).sum())
r=claims.merge(policies[["policy_id","effective_date","expiration_date"]],on="policy_id",how="left"); detected["CLAIM_OUTSIDE_POLICY_TERM"]=int((r.effective_date.notna()&(r.expiration_date>=r.effective_date)&((r.claim_date<r.effective_date)|(r.claim_date>r.expiration_date))).sum()); detected["NONPOSITIVE_WRITTEN_PREMIUM"]=int((premiums.written_premium<=0).sum()); detected["INVALID_VEHICLE_MODEL_YEAR"]=int(((vehicles.model_year<1980)|(vehicles.model_year>2026)).sum())
assert m.exception_type.value_counts().to_dict()==detected and sum(detected.values())==1200
for name,df in {"quotes.csv":quotes,"policies.csv":policies,"vehicles.csv":vehicles,"premiums.csv":premiums,"claims.csv":claims,"exception_manifest.csv":m}.items(): df.to_csv(OUT/name,index=False,date_format="%Y-%m-%d")
s=pd.DataFrame([{"exception_type":k,"exception_count":v} for k,v in detected.items()]); s.loc[len(s)]=["TOTAL",sum(detected.values())]; s.to_csv(OUT/"exception_summary.csv",index=False)
print(f"Generated {len(quotes):,} quotes, {len(policies):,} policies, {len(vehicles):,} vehicles, {len(claims):,} claims and {sum(detected.values()):,} validated exceptions.")
