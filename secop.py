# Global variables
codeCategory = 'V1.811022%'
useFilterKeywords = True
# Create a list of keywords
keywords = [
    "Estudio de demanda", "Plan Maestro de Movilidad", "Estudio de movilidad",
    "Plan infraestructura", "plan local de seguridad vial", "Plan intermodal",
    "Modelo de transporte", "Encuesta origen destino",
    "Toma informacion de campo", "Caracterizacion de vías",
    "Estudio de tránsito", "Diseño Señalización",
    "Planes Estratégicos de Seguridad Vial", "Auditorias de seguridad vial",
    "Capacitacion seguridad vial", "Plan de Manejo de Tránsito",
    "Diseño semafórico", "Cartografia", "Desarrollo web", "estrategia digital",
    "Diseño urbano", "Wayfinding", "diseño de información", "Estrategia",
    "políticas públicas", "Estudios de comportamiento",
    "Planificación de desarrollos", "Planificación de infraestructura",
    "Analítica espacial", "Recaudación", "gestión de tarifas"
]
# Create a pattern that matches any of the keywords
pattern = '|'.join(keywords)

import requests
import pandas as pd
from typing import List, Dict, Any, Tuple
from time import sleep
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor


class SecopDataFetcher:

    def __init__(self, url: str, is_secop_ii: bool = True):
        self.url = url
        self.is_secop_ii = is_secop_ii
        self.code_category_field = 'codigo_principal_de_categoria' if is_secop_ii else 'codigo_de_categoria_principal'
        self.phase_condition = "fase = 'Presentación de oferta'" if is_secop_ii else ""

    def get_total_records(self) -> int:
        """Get total number of records matching the filter criteria."""
        where_clause = f"WHERE {self.code_category_field} LIKE '{codeCategory}'"
        if self.phase_condition:
            where_clause += f" AND {self.phase_condition}"

        count_query = f"SELECT count(*) {where_clause}"

        try:
            response = requests.get(self.url, params={"$query": count_query})
            response.raise_for_status()
            total_records = int(response.json()[0]['count'])
            print(f"Total records to fetch: {total_records}")
            return total_records
        except Exception as e:
            print(f"Error getting record count: {e}")
            return 0

    def fetch_page(self, params: Tuple[int, int]) -> List[Dict[str, Any]]:
        """Fetch a single page of data."""
        offset, page_size = params
        where_clause = f"WHERE {self.code_category_field} LIKE '{codeCategory}'"
        if self.phase_condition:
            where_clause += f" AND {self.phase_condition}"

        order_by = "fecha_de_publicacion DESC" if self.is_secop_ii else "fecha_de_firma DESC NULLS LAST"

        query = f"""
        SELECT * 
        {where_clause}
        ORDER BY {order_by}
        LIMIT {page_size}
        OFFSET {offset}
        """

        try:
            response = requests.get(self.url, params={"$query": query})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching data at offset {offset}: {e}")
            return []

    def fetch_all_data(self, page_size: int = 1000) -> List[Dict[str, Any]]:
        """Fetch all data using parallel requests."""
        total_records = self.get_total_records()
        if not total_records:
            return []

        # Create parameters for each page
        params = [(offset, page_size)
                  for offset in range(0, total_records, page_size)]
        all_data = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            for i, data in enumerate(executor.map(self.fetch_page, params)):
                all_data.extend(data)
                records_fetched = min((i + 1) * page_size, total_records)
                print(f"Progress: {records_fetched}/{total_records} records "
                      f"({(records_fetched/total_records*100):.1f}%)")
                sleep(0.2)  # Rate limiting

        print(f"Total records fetched: {len(all_data)}")
        return all_data


def process_data(data: List[Dict[str, Any]],
                 is_secop_ii: bool = True) -> pd.DataFrame:
    """Process the raw data into a DataFrame."""
    if not data:
        print("No data to process")
        return pd.DataFrame()

    df = pd.DataFrame(data)

    # Convert date columns
    date_columns = [col for col in df.columns if 'fecha' in col.lower()]
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    # Define numeric columns based on SECOP version
    if is_secop_ii:
        numeric_columns = [
            'precio_base', 'valor_total_adjudicacion', 'duracion',
            'proveedores_invitados', 'proveedores_con_invitacion',
            'visualizaciones_del', 'proveedores_que_manifestaron',
            'respuestas_al_procedimiento', 'respuestas_externas',
            'conteo_de_respuestas_a_ofertas', 'proveedores_unicos_con',
            'numero_de_lotes'
        ]
    else:
        numeric_columns = ['dias_adicionados', 'duraci_n_del_contrato']
        # Add monetary columns
        numeric_columns.extend([
            col for col in df.columns
            if 'valor' in col.lower() or 'saldo' in col.lower()
        ])

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Apply keyword filter if enabled
    if useFilterKeywords:
        desc_field = 'descripci_n_del_procedimiento' if is_secop_ii else 'descripcion_del_proceso'
        df = df[df[desc_field].str.contains(pattern,
                                            case=False,
                                            na=False,
                                            regex=True)]

    return df


def save_to_csv(df: pd.DataFrame, prefix: str):
    """Save DataFrame to CSV with timestamp."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{prefix}_{timestamp}.csv'
    df.to_csv(filename, index=False)
    print(f"\nData saved to '{filename}'")


def fetch_and_process_all_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Main function to fetch and process data from both SECOP II Open and II Closed."""
    secop_ii_open_fetcher = SecopDataFetcher(
        "https://www.datos.gov.co/resource/p6dx-8zbt.json", True)
    secop_ii_closed_fetcher = SecopDataFetcher(
        "https://www.datos.gov.co/resource/jbjy-vk9h.json", False)

    # Fetch and process SECOP II data
    print("\nProcessing SECOP II Open data...")
    secop_ii_data = secop_ii_open_fetcher.fetch_all_data()
    df_secop_ii_open = process_data(secop_ii_data, True)
    if not df_secop_ii_open.empty:
        save_to_csv(df_secop_ii_open, 'secop_ii_open')
        generate_category_summary(df_secop_ii_open)

    # Fetch and process SECOP I data
    print("\nProcessing SECOP II Closed data...")
    secop_i_data = secop_ii_closed_fetcher.fetch_all_data()
    df_secop_ii_closed = process_data(secop_i_data, False)
    if not df_secop_ii_closed.empty:
        save_to_csv(df_secop_ii_closed, 'secop_ii_closed')
        generate_transport_summary(df_secop_ii_closed)

    return df_secop_ii_open, df_secop_ii_closed


# Keep the original summary generation functions unchanged
def generate_category_summary(df: pd.DataFrame) -> None:
    """Generates and prints a comprehensive summary of the filtered data."""
    print(
        "\n=== SECOP II Analysis - Presentation Phase Transportation Services ==="
    )

    # Basic Statistics
    print("\n1. General Statistics:")
    print(f"Total number of procedures: {len(df):,}")
    print(
        f"Unique category codes: {df['codigo_principal_de_categoria'].nunique()}"
    )
    print("\nCategory code distribution:")
    print(df['codigo_principal_de_categoria'].value_counts())

    # [Rest of the function remains exactly the same as in your original code]
    # ... [Previous implementation]


def generate_transport_summary(df: pd.DataFrame) -> None:
    """Generates and prints a comprehensive summary of active transport contracts."""
    print("\n=== Active Transport Contracts Summary ===")
    print(f"Total number of active transport contracts: {len(df):,}")

    # [Rest of the function remains exactly the same as in your original code]
    # ... [Previous implementation]


if __name__ == "__main__":
    df_secop_ii_open, df_secop_ii_closed = fetch_and_process_all_data()

    # Additional verification for SECOP II
    if not df_secop_ii_closed.empty:
        print("\nVerification of category codes in the SECOP II dataset:")
        print("\nUnique category codes:")
        print(df_secop_ii_closed['codigo_principal_de_categoria'].unique())
        print("\nDistribution of category codes:")
        print(
            df_secop_ii_closed['codigo_principal_de_categoria'].value_counts())
