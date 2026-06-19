cat > docs/cost_model_assumptions.md << 'EOF'
# Cost Model Assumptions

## From real data (this project's dataset)
- Fraud rate: 3.499% (590,540 transactions, 20,663 labeled fraud)
- Source: IEEE-CIS Fraud Detection dataset (Kaggle)

## From industry research (not derived from this dataset)
- False decline rate cost ratio: ~9x fraud loss, per Section 2 of the project manual
- Customer churn after false decline: ~39% (cited industry figure)

These industry figures are used to weight the cost function in Section 2,
since the IEEE-CIS dataset has no churn or lifetime-value data of its own.
EOF