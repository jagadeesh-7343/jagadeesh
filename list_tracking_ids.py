import psycopg2


def main():
    conn = psycopg2.connect(
        dbname="citizen_bridge",
        user="postgres",
        password="nsrit",
        host="localhost",
        port="5432",
    )
    cur = conn.cursor()

    departments = ["education", "police", "health", "electrical", "transport"]

    for dept in departments:
        table = f"complaints_{dept}"
        cur.execute(
            f"""
            SELECT id, tracking_id, status, COALESCE(problem_description, '')
            FROM {table}
            ORDER BY id
            """
        )
        rows = cur.fetchall()

        print(f"\n=== {dept.upper()} ===")
        if not rows:
            print("No complaints")
            continue

        for complaint_id, tracking_id, status, description in rows:
            issue = (description or "").replace("\n", " ").strip()
            if len(issue) > 55:
                issue = issue[:55] + "..."
            print(
                f"id={complaint_id} | tracking_id={tracking_id} | status={status} | issue={issue}"
            )

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
