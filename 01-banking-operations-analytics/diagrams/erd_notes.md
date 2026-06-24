# ERD Notes

## Core Entity Flow

Customer → Account → Transaction

## Supporting Entities

Product → Account  
Branch → Account  
Branch → Transaction  
Channel → Transaction  
Customer → Complaint  
Complaint → SLA Ticket  
Customer → Campaign  

## Planned Dimensions

- dim_customer
- dim_account
- dim_product
- dim_branch
- dim_channel
- dim_date

## Planned Facts

- fact_transactions
- fact_complaints
- fact_campaigns
- fact_sla_tickets
