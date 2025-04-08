import pandas as pd
import numpy as np
from io import BytesIO
import datetime
from datetime import timedelta

def generate_test_excel(filename="test_data.xlsx", num_rows=100):
    """
    Generates a sample Excel file with a specified number of rows of data
    suitable for testing the FinFlow Pro app.

    Args:
        filename (str, optional): The name of the Excel file to generate.
                                 Defaults to "test_data.xlsx".
        num_rows (int, optional): The number of rows of data to generate.
                                Defaults to 100.
    """

    # Generate dates over a period
    start_date = datetime.date(2023, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(num_rows)]

    # Generate random values
    values = np.random.uniform(-1000, 2000, num_rows)

    # Generate types (Receita or Despesa)
    types = np.random.choice(['Receita', 'Despesa'], num_rows)

    # Generate categories
    categories = np.random.choice(
        ['Vendas', 'Serviços', 'Aluguel', 'Salários', 'Marketing', 'Outros'],
        num_rows
    )

    # Generate descriptions (simple for now)
    descriptions = [f'Transação {i+1}' for i in range(num_rows)]

    data = {
        'Data': dates,
        'Valor': values,
        'Tipo': types,
        'Categoria': categories,
        'Descrição': descriptions
    }

    df = pd.DataFrame(data)
    df['Data'] = pd.to_datetime(df['Data'])  # Ensure 'Data' is datetime

    df.to_excel(filename, index=False)
    print(f"Arquivo '{filename}' com {num_rows} linhas gerado com sucesso.")


if __name__ == "__main__":
    generate_test_excel(num_rows=150) # You can change num_rows here