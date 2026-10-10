def generate_report(customer_id, spending_data):
    # Select the customer's spending information
    customer_report = spending_data.loc[customer_id]

    # Calculate total spending across all categories
    total_spending = customer_report["total_spending"].sum()

    # Return a structured financial report
    return {
        "customer_id": customer_id,
        "total_spending": round(float(total_spending), 2),
        "categories": customer_report.to_dict(orient="index"),
    }
