# Evaluation results (offline deterministic baseline)

## dev set (sample_leads.json)

| metric | value |
|---|---|
| n_leads | 17 |
| intent_accuracy | 1.0 |
| tier_accuracy | 1.0 |
| service_line_accuracy | 1.0 |
| retrieval_hit_rate | 1.0 |

| id | expected intent | predicted intent | expected tier | predicted tier | score | status |
|---|---|---|---|---|---|---|
| L01 | new_project | new_project | HOT | HOT | 87 | OK |
| L02 | new_project | new_project | WARM | WARM | 62 | OK |
| L03 | new_project | new_project | COLD | COLD | 28 | OK |
| L04 | product_demo | product_demo | HOT | HOT | 75 | OK |
| L05 | training | training | WARM | WARM | 48 | OK |
| L06 | career | career | NOT_A_PROSPECT | NOT_A_PROSPECT | 0 | OK |
| L07 | vendor_solicitation | vendor_solicitation | NOT_A_PROSPECT | NOT_A_PROSPECT | 0 | OK |
| L08 | spam_or_irrelevant | spam_or_irrelevant | NOT_A_PROSPECT | NOT_A_PROSPECT | 0 | OK |
| L09 | new_project | new_project | HOT | HOT | 95 | OK |
| L10 | new_project | new_project | WARM | WARM | 54 | OK |
| L11 | unclear | unclear | COLD | COLD | 8 | OK |
| L12 | product_demo | product_demo | HOT | HOT | 75 | OK |
| L13 | new_project | new_project | HOT | HOT | 74 | OK |
| L14 | new_project | new_project | WARM | WARM | 52 | OK |
| L15 | new_project | new_project | COLD | COLD | 43 | OK |
| L16 | new_project | new_project | WARM | WARM | 60 | OK |
| L17 | new_project | new_project | COLD | COLD | 28 | OK |

## holdout set (holdout_leads.json)

| metric | value |
|---|---|
| n_leads | 10 |
| intent_accuracy | 0.5 |
| tier_accuracy | 0.6 |
| service_line_accuracy | 0.5 |
| retrieval_hit_rate | 0.6 |

| id | expected intent | predicted intent | expected tier | predicted tier | score | status |
|---|---|---|---|---|---|---|
| H01 | new_project | unclear | HOT | WARM | 50 | MISS |
| H02 | new_project | new_project | WARM | WARM | 40 | OK |
| H03 | training | training | COLD | COLD | 21 | OK |
| H04 | new_project | new_project | WARM | WARM | 60 | OK |
| H05 | vendor_solicitation | unclear | NOT_A_PROSPECT | COLD | 20 | MISS |
| H06 | product_demo | unclear | WARM | COLD | 20 | MISS |
| H07 | new_project | unclear | COLD | COLD | 8 | MISS |
| H08 | new_project | unclear | HOT | COLD | 35 | MISS |
| H09 | new_project | new_project | WARM | WARM | 55 | OK |
| H10 | unclear | unclear | COLD | COLD | 20 | OK |
