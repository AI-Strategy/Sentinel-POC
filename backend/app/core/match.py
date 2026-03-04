import json
import logging
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

class EntityMapper:
    def __init__(self, api_key: str):
        # We assume the new google-genai SDK 2.0 is used as per user architecture.
        self.client = genai.Client(api_key=api_key)

    def generate_mapping(self, invoices: list, pos: list, pods: list) -> dict:
        """
        Uses Gemini Flash to resolve disparate identifiers into a canonical ID.
        Strictly replaces fragile Regex matching.
        """
        try:
            skus = list(set([i['sku'] for i in invoices]))
            item_refs = list(set([p['item_reference'] for p in pos]))
            part_ids = list(set([d['part_id'] for d in pods]))

            prompt = f"""
            Map the following disparate inventory identifiers to a single canonical ID based on semantic similarity.
            SKUs: {skus}
            Item References: {item_refs}
            Part IDs: {part_ids}
            
            Return ONLY a JSON dictionary where keys are the raw identifiers (SKU, Item Ref, or Part ID) and values are a unified canonical string name. 
            Example: {{"SKU-123-BLK": "WIDGET_A", "REF_WIDGET_A": "WIDGET_A"}}
            """

            # Using gemini-2.0-flash (most stable current version of Flash)
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            
            mapping = json.loads(response.text)
            logger.info("Semantic mapping generated for %d entities", len(mapping))
            return mapping
        except Exception as e:
            logger.error(f"Entity matching failed: {e}")
            # Fallback to identity mapping if LLM fails
            fallback = {}
            for s in skus: fallback[s] = s
            for p in item_refs: fallback[p] = p
            for pt in part_ids: fallback[pt] = pt
            return fallback
