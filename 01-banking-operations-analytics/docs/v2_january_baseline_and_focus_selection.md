# V2 January Baseline and Focus Selection

## 1. Purpose

Establish the January operating baseline and select the Mobile Banking product and customer segment that will form the focus of Version 2.

## 2. Data Coverage

- Transactions: 25,000 records from 2026-01-01 through 2026-01-31.
- Complaints: 2,000 records across January and February 2026; January contains 1,044 complaints.
- Campaigns: 5,000 records across January and February 2026.
- SLA tickets: 4,000 records across January to March 2026 because some tickets were created after the originating complaint month.
- Important coverage limitation: the fact tables do not all share the same monthly coverage. January is therefore used as the controlled transaction baseline, while complaint and SLA analysis uses complaint-month cohorts and retains legitimate later ticket creation.

## 3. Overall January Transaction Baseline

| KPI | January result |
|---|---:|
| Total transactions | 25,000 |
| Distinct customers | Pending capture from Section 7 output |
| Successful transactions | 23,025 |
| Failed transactions | 1,483 |
| Reversed transactions | 492 |
| Success rate | 92.10% |
| Failure rate | 5.93% |
| Reversal rate | 1.97% |
| Total transaction amount | 95,700,601.35 |

The January status counts reconcile exactly: 23,025 successful + 1,483 failed + 492 reversed = 25,000 total transactions.

## 4. Mobile Banking vs Internet Banking

| Channel | Distinct customers | Transactions | Failed | Reversed | Failure rate | Reversal rate | Total amount | Failed amount | Reversed amount |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Mobile Banking | 3,061 | 4,210 | 244 | 91 | 5.80% | 2.16% | 161,762,828.00 | 10,142,305.66 | 3,420,916.18 |
| Internet Banking | 2,999 | 4,178 | 260 | 87 | 6.22% | 2.08% | 160,752,720.00 | 9,671,975.93 | 3,211,181.61 |

Internet Banking has the higher January failure rate and failed count. Mobile Banking, however, has slightly higher transaction volume, more distinct customers, a higher reversal rate, and the highest complaint burden among all channels. Mobile Banking is therefore selected as the V2 channel because it offers the stronger combined transaction, customer-experience, complaint, and SLA analysis story.

## 5. Mobile Banking Product Exposure

| Product | Volume | Volume share | Failed | Reversed | Failure rate | Failed amount | Reversed amount | Failure share |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Savings Account | 1,378 | 32.73% | 78 | 31 | 5.66% | 3,246,577.34 | 1,168,389.10 | 31.97% |
| Salary Account | 1,100 | 26.13% | 60 | 24 | 5.45% | 2,288,460.07 | 1,004,555.96 | 24.59% |
| Credit Card | 479 | 11.38% | 38 | 6 | 7.93% | 1,604,579.13 | 272,672.48 | 15.57% |
| Fixed Deposit | 501 | 11.90% | 25 | 15 | 4.99% | 1,312,935.60 | 623,542.69 | 10.25% |
| Current Account | 403 | 9.57% | 21 | 8 | 5.21% | 744,023.24 | 263,536.78 | 8.61% |
| Personal Loan | 261 | 6.20% | 17 | 5 | 6.51% | 650,362.53 | 77,167.15 | 6.97% |
| Home Loan | 88 | 2.09% | 5 | 2 | 5.68% | 295,367.75 | 11,052.02 | 2.05% |

Savings Account is the strongest product candidate because it has the highest Mobile Banking volume, the largest failed and reversed counts, the largest affected value, and nearly one-third of all Mobile Banking failures.

## 6. Mobile Banking Customer-Segment Exposure

| Segment | Customers | Volume | Volume share | Failed | Reversed | Failure rate | Failed amount | Reversed amount | Failure share |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Mass | 2,219 | 3,072 | 72.97% | 169 | 64 | 5.50% | 6,375,453.61 | 2,616,255.52 | 69.26% |
| Affluent | 661 | 892 | 21.19% | 63 | 19 | 7.06% | 2,898,042.24 | 652,903.43 | 25.82% |
| Premium | 181 | 246 | 5.84% | 12 | 8 | 4.88% | 868,809.81 | 151,757.23 | 4.92% |

Affluent customers have the highest failure rate, but the Mass segment carries far greater operational exposure: almost 73% of Mobile Banking volume, 169 failed transactions, 64 reversals, and 69.26% of all Mobile Banking failures.

## 7. Product × Segment Concentration

The strongest combined concentration is **Savings Account × Mass**:

- 803 distinct customers
- 983 transactions
- 23.35% of all Mobile Banking volume
- 50 failed transactions
- 19 reversals
- 69 affected transactions
- 20.49% of all Mobile Banking failures
- 2,695,401.77 in affected transaction value
- 43 complaints
- 43.74 complaints per 1,000 transactions
- 97 associated SLA tickets
- 21 breached SLA tickets
- 21.65% SLA breach rate

Salary Account × Mass is a close secondary candidate with 67 affected transactions and a slightly higher affected value of 2,788,252.84, but Savings Account × Mass has higher volume, more affected transactions, more complaints, and more SLA tickets.

## 8. Complaint and SLA Impact

### Overall January complaint baseline

| KPI | Result |
|---|---:|
| Total complaints | 1,044 |
| Resolved complaints | 711 |
| Unresolved complaints | 333 |
| Complaint resolution rate | 68.10% |
| Average resolution days | 5.35 |
| High-priority complaints | 215 |
| Complaints with SLA tickets | 927 |
| Complaints without SLA tickets | 117 |
| Total associated SLA tickets | 2,114 |

### Channel comparison

| Channel | Complaints | Resolution rate | Average resolution days | High-priority complaints | Complaints with SLA tickets | SLA tickets | Complaints per 1,000 transactions |
|---|---:|---:|---:|---:|---:|---:|---:|
| Mobile Banking | 195 | 67.69% | 5.64 | 43 | 176 | 413 | 46.32 |
| Internet Banking | 170 | 70.59% | 4.73 | 30 | 150 | 352 | 40.69 |

Mobile Banking has the highest complaint volume and the highest normalized complaint rate among the channels analysed. It also has a lower resolution rate, longer average resolution time, and more associated SLA tickets than Internet Banking.

### Focus combination service impact

For Savings Account × Mass:

- Complaint count: 43
- Complaint resolution rate: 65.12%
- Average resolution time: 6.18 days
- SLA-ticket count: 97
- SLA-breached tickets: 21
- SLA-breach rate: 21.65%

These service metrics support the product-segment selection, while remaining an aggregated operational association rather than proof that each complaint was caused by a specific transaction.

## 9. Focus Selection

### Selected channel

**Mobile Banking**

### Selected product

**Savings Account**

### Selected customer segment

**Mass**

### Evidence supporting the selection

- **Sufficient transaction volume:** Savings Account × Mass contains 983 transactions, representing 23.35% of Mobile Banking volume. The Mass segment represents 72.97% of all Mobile Banking transactions.
- **Failed/reversed transaction exposure:** The combination records 50 failures and 19 reversals, the highest affected count among product-segment combinations.
- **Affected transaction value:** Failed and reversed transactions total 2,695,401.77 in affected value.
- **Complaint impact:** The combination has 43 complaints and 43.74 complaints per 1,000 transactions. Mobile Banking overall has the highest channel complaint rate at 46.32 per 1,000 transactions.
- **SLA impact:** The combination generates 97 SLA tickets, of which 21 breach SLA, producing a 21.65% breach rate.
- **Business relevance:** Savings accounts are high-volume, recurring-use products, and the Mass segment represents the broadest customer population. A reliability issue here would have visible operational and customer-experience consequences.

## 10. Limitations

- No direct transaction-to-complaint linkage exists in V1.
- Complaint rates are aggregated channel/product/segment operational associations.
- January data is a baseline and does not prove causality.
- Some product-segment combinations have small complaint or ticket populations; extreme rates for those groups should not outweigh volume and absolute impact.
- The source facts have inconsistent monthly coverage, so complaint and SLA metrics are calculated using complaint-month cohorts rather than assuming every fact is January-only.
- The data is synthetic; findings demonstrate analytical design and decision logic rather than a live banking outcome.

## 11. February Design Dependency

February incident assumptions should now be synthesized around **Mobile Banking × Savings Account × Mass customers**.

The February scenario should increase failures and reversals for this focus population on selected incident dates, followed by higher relevant complaint volume and Digital Support SLA pressure. March should simulate partial technical recovery and a controlled service-recovery experiment. Exact February and March targets should be calibrated against the January values documented above rather than chosen independently.
