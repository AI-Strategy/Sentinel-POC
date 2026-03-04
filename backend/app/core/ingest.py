import json
import csv
import xml.etree.ElementTree as ET
from pathlib import Path

class Ingestor:
    @staticmethod
    def ingest_invoice(filepath: str | Path) -> list[dict]:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Corrupted JSON in {filepath}. Error: {e}")

    @staticmethod
    def ingest_po(filepath: str | Path) -> list[dict]:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return [row for row in reader]
        except Exception as e:
            raise ValueError(f"Failed to read CSV in {filepath}. Error: {e}")

    @staticmethod
    def ingest_pod(filepath: str | Path) -> list[dict]:
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            pods = []
            for item in root.findall('waybill'):
                pods.append({
                    "waybill_ref": item.find('waybill_ref').text,
                    "qty_received_at_dock": int(item.find('qty_received_at_dock').text),
                    "part_id": item.find('part_id').text,
                    "condition": item.find('condition').text
                })
            return pods
        except ET.ParseError as e:
            raise ValueError(f"Corrupted XML in {filepath}. Error: {e}")
        except Exception as e:
            raise ValueError(f"Failed to process XML {filepath}. Error: {e}")
