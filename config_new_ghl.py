"""
Config GHL nuovo account (Unlimited $297)
Creato automaticamente il 2026-04-08

Struttura: 5 sub-account separati, uno per setter/cliente.
Le pipeline usano gli stage di default GHL — rinominali in GHL UI:
  New Lead       → Lead Nuovo
  Contacted      → AI Qualifica
  Qualified      → Setter Chiama
  Proposal Sent  → Appuntamento
  Negotiation    → Closer / Demo
  Closed         → Chiuso Vinto
  (aggiungi manualmente) → Nurture
"""

import os

# ─── ACCOUNT PRINCIPALE (default location) ────────────────────────────────────
GHL_TOKEN_DEFAULT   = os.getenv("GHL_API_KEY_NEW", "pit-591f3c04-3bd6-4298-b50e-10706725730f")
GHL_LOCATION_DEFAULT = "MmTjhou61wLMd2f5aO5b"

# ─── SUB-ACCOUNT PER SETTER ───────────────────────────────────────────────────
# Struttura: { setter_name: { token, loc, pipeline_id, stage_ids, field_ids } }

SUBACCOUNTS = {

    "adriana": {
        "token":       os.getenv("GHL_TOKEN_ADRIANA", "pit-40ba01ad-4fd9-4efa-a485-2b65b01faee3"),
        "loc":         "CMZlV7vFh1d8zDey33ST",
        "pipeline_id": "5L36iGxRxuiY735F8ptg",
        "stages": {
            "lead_nuovo":    "268e87ee-626b-4c40-98e9-0f99e043119f",  # New Lead
            "ai_qualifica":  "57c3d945-b0f8-4044-bdb1-b1d72053a594",  # Contacted
            "setter_chiama": "d9ce4112-74a7-4e26-806e-2d8db3816739",  # Qualified
            "appuntamento":  "68c53cf6-e320-4426-a1bd-214bc08b15f7",  # Proposal Sent
            "closer_demo":   "0929894a-fa43-4a3e-bb70-0357dc43b851",  # Negotiation
            "chiuso_vinto":  "0e36b8a6-3610-488d-aabd-bcfa6a69fc91",  # Closed
        },
        "fields": {
            "Esito AI Call":           "mNYQwlCxBzOmV241TQUN",
            "Operatore Assegnato":     "yojJxnoEcpUXNxtFsJz8",
            "Cliente Assegnato":       "IGMXU4STF9h7Q41KqeJO",
            "Score Lead":              "oQhoZqAMwKj632kHL7UN",
            "Fonte Lead":              "WlkbcbItr5H9Nkxdpqhy",
            "Canale":                  "87eH8vOeDMg0r0qzZp3B",
            "Batch ElevenLabs":        "x7xPZoD5GbfFrBBHP4bz",
            "Recording URL":           "bRji51JVDRy6OiqtDxe5",
            "Durata Chiamata":         "ks94tixyjAqsIYMVNB2B",
            "Riassunto AI":            "La5nsqJ5PNqJNy5Wvajk",
            "Note Chiamata":           "hWmIgZYXOzYAzIhoQdlM",
            "Email Referente":         "tHnGdI6Td9FbJoNFMwnB",
            "Nome Referente":          "rtsfKVqNwtWkZCZ8BFlY",
            "Data Ultimo Contatto":    "Y05uQhzkrkjdLqRFOKdx",
            "Data Prossima Chiamata":  "ECKe903rphNIpmHoLjFH",
        },
    },

    "claudia": {
        "token":       os.getenv("GHL_TOKEN_CLAUDIA", "pit-10526992-12ab-493f-bfda-c6bad2ea5d47"),
        "loc":         "dxaIcnpST8sTdACjtawU",
        "pipeline_id": "O5nDv8n4jMl9Esa7Bbr4",
        "stages": {
            "lead_nuovo":    "335caceb-8884-4092-9587-22dd1e87a98f",
            "ai_qualifica":  "b5cffc75-89d0-4138-891e-ef71be90ec4d",
            "setter_chiama": "ab632632-6e2a-43b6-abd9-e2ef36df040e",
            "appuntamento":  "a068df6a-c94a-4795-9e77-070403c2b980",
            "closer_demo":   "1aa4d1fd-3760-47ee-a2a1-395a34800717",
            "chiuso_vinto":  "b699e9a0-0e7e-4a3c-9f1d-2b3c4d5e6f7a",
        },
        "fields": {
            "Esito AI Call":           "DZ0SuDLmXV3XtmcNookX",
            "Operatore Assegnato":     "OobaiscHMxG91dhFguWF",
            "Cliente Assegnato":       "3iKu7BFHIkGniYMjbJiG",
            "Score Lead":              "D6U8G8zkw4R569C2aoBs",
            "Fonte Lead":              "DWYebhtfpBgeRTZLGBzK",
            "Canale":                  "2Ti2EDnPpg23mtcI6H5B",
            "Batch ElevenLabs":        "dChIx4JX44l1S89C6VTr",
            "Recording URL":           "dnc5ltL1vE1PPgPVNrq0",
            "Durata Chiamata":         "3exbaPkAYPuFWwUICnBY",
            "Riassunto AI":            "IPjctxWksWvSAYYJMnN8",
            "Note Chiamata":           "VL1w0MaTJKaweJ3VKnnY",
            "Email Referente":         "AvQUl25dlssGSZKuZJMv",
            "Nome Referente":          "ydbd6otKxuTfmoMACvcx",
            "Data Ultimo Contatto":    "RIkijcXBQA54rLfBxcF3",
            "Data Prossima Chiamata":  "XiHFAteXgLPCj9C6Id6S",
        },
    },

    "edoardo": {
        "token":       os.getenv("GHL_TOKEN_EDOARDO", "pit-ab65172d-61b8-4730-b766-513a6f8b47bc"),
        "loc":         "gRLsJElqoGRgg7LJvOwP",
        "pipeline_id": "5jcRdmDHtwu6tTvsGy7Q",
        "stages": {
            "lead_nuovo":    "53118a8e-c3f9-46e9-944c-ceecc64a0b80",
            "ai_qualifica":  "24b0c4f0-d862-491f-9a4e-f8fe64270ddc",
            "setter_chiama": "a782296e-dcc2-4816-bc91-f8132e097a2e",
            "appuntamento":  "7ce6ed73-fa8b-4952-ae21-18b7213706cd",
            "closer_demo":   "85a2c49d-9625-405c-b590-ce2c0ed25522",
            "chiuso_vinto":  "a783d4c2-ad6a-4f9e-8c4b-35128107d2f9",
        },
        "fields": {
            "Esito AI Call":           "pm54BrSo1k8n6bA0blCc",
            "Operatore Assegnato":     "fbVnrAxTZDBYuzJBToDb",
            "Cliente Assegnato":       "zCd9cOyXu2gGFJgz2G1i",
            "Score Lead":              "ERAp6aN31uhOqyMgo67q",
            "Fonte Lead":              "P2c2gfHctp7qhV5dBSE2",
            "Canale":                  "aDIlcOiVEx7YLeaDSykr",
            "Batch ElevenLabs":        "4LiAlwPx37aEPpR33dCp",
            "Recording URL":           "ejqbTrzjYaP0zQlP2ozf",
            "Durata Chiamata":         "EVQwLD9B4nUBQHpzdZ0H",
            "Riassunto AI":            "nFAo14Qjzc8FVtYPANwY",
            "Note Chiamata":           "W0TLTT9Ty8mIG5RJ2ViO",
            "Email Referente":         "X0FlTLXMTO1aPg5lyZz9",
            "Nome Referente":          "WohtWFBItfc9rlzhuUaH",
            "Data Ultimo Contatto":    "fWMdIZD9F22SjiprfwqY",
            "Data Prossima Chiamata":  "kvFEhflJafosXew7hWHS",
        },
    },

    "filippo": {
        "token":       os.getenv("GHL_TOKEN_FILIPPO", "pit-bcf8cb1d-4a8d-48a7-8fad-0618c599b0f9"),
        "loc":         "00ymdougVPINOEMGs4ao",
        "pipeline_id": "kFztQkd6NC6sS4LoegZz",
        "stages": {
            "lead_nuovo":    "2ad65e6e-88dc-418c-991e-254e67f3c4ee",
            "ai_qualifica":  "67b9e16d-928b-4299-9ac3-417c376736a9",
            "setter_chiama": "111c4d77-6b56-4f89-80fa-00701085a557",
            "appuntamento":  "bbc2720e-bba8-4301-9a1c-d6ce20ca3511",
            "closer_demo":   "bdb6fe6c-5638-4b48-b1cb-7e47d5ba9327",
            "chiuso_vinto":  "cc170258-2548-4061-b5c5-2223b57ac8a5",
        },
        "fields": {
            "Esito AI Call":           "Tsn1so1q2CytPq69EtLB",
            "Operatore Assegnato":     "jJI8O5n6TSQOEvJx8jMP",
            "Cliente Assegnato":       "SEUmGkL7L4QP9poLSlWf",
            "Score Lead":              "Dl6AylQIbTNYMHHRgs9W",
            "Fonte Lead":              "8S43elQiybPjm48GZaMO",
            "Canale":                  "tSYzfSFao9zIkgOY2A2t",
            "Batch ElevenLabs":        "I6DspVCKQZbp5SwMZQFR",
            "Recording URL":           "7GStIpnwpFY4yDNdvX8x",
            "Durata Chiamata":         "C0MYhUsSH2qqadntVAkf",
            "Riassunto AI":            "bEkrtssLnAJLM7y3nMDY",
            "Note Chiamata":           "i8vBPmO7PPstS8zlVtys",
            "Email Referente":         "FMNJElKUyKNP4nZEsDRS",
            "Nome Referente":          "ohXuCpV58IDyB6XSLmio",
            "Data Ultimo Contatto":    "yhBYXnawvReK9gSTg5bF",
            "Data Prossima Chiamata":  "re1NUzYIqMPrYBLCbGXE",
        },
    },

    "laura": {
        "token":       os.getenv("GHL_TOKEN_LAURA", "pit-fa43377f-b632-469d-a510-f41a034b6821"),
        "loc":         "iXNMuVl88CJ7u7z7wBto",
        "pipeline_id": "9m9jEt8GEtx4sibfA99O",
        "stages": {
            "lead_nuovo":    "ae62701f-e76c-427a-a897-14549b7132b4",
            "ai_qualifica":  "537d70ea-3e17-4b4c-82ed-0f56213d3b09",
            "setter_chiama": "e70f9252-a8f2-4125-9acc-d1d123554504",
            "appuntamento":  "c79d3c5c-24d5-47bd-af4e-715508d3612c",
            "closer_demo":   "51140335-6984-4e0d-87ff-28e2763b7152",
            "chiuso_vinto":  "24d7fa98-de1c-4eb6-937d-00a02d269b83",
        },
        "fields": {
            "Esito AI Call":           "Od3m6zzCv91ayvmyc3Hp",
            "Operatore Assegnato":     "pnv6m6NfKEtGq0R4tKgk",
            "Cliente Assegnato":       "WMtY2hXWwDW0XhwHmms5",
            "Score Lead":              "ve7ftFtYnC7qiooP1nhu",
            "Fonte Lead":              "zYsq09Sqi8OOLSlrG06N",
            "Canale":                  "ExBMxfDAPjVcwmApesil",
            "Batch ElevenLabs":        "ddkP2R0UPRtLEBbVbKlG",
            "Recording URL":           "gyWF3LogzcFG41IdeMfx",
            "Durata Chiamata":         "XQh3DZjYANwUWbotoOhB",
            "Riassunto AI":            "dIrdiWEsMVZLtkm7dHPV",
            "Note Chiamata":           "Pz8NLIEC8pAocvlDQ8xc",
            "Email Referente":         "vSY9s7BHBKvEjxf0UAga",
            "Nome Referente":          "ytNsVhs5vvm1Y54HxCdo",
            "Data Ultimo Contatto":    "hG1jfpy2CXinu1agd8n9",
            "Data Prossima Chiamata":  "BdBFmYutAKjlKusL8LSB",
        },
    },
}

# ─── MAPPINGS ─────────────────────────────────────────────────────────────────

# interest_level → stage key
INTEREST_TO_STAGE_KEY = {
    "appointment": "appuntamento",
    "high":        "setter_chiama",
    "medium":      "ai_qualifica",
    "low":         "lead_nuovo",
    "none":        None,
}

# interest_level → Esito AI Call value
ESITO_TO_GHL = {
    "appointment": "Appuntamento Fissato",
    "high":        "Interessato",
    "medium":      "Email Fornita",
    "low":         "Non Interessato",
    "none":        "Non Risposto / IVR",
}

# interest_level → Score Lead
INTEREST_TO_SCORE = {
    "appointment": 100,
    "high":        75,
    "medium":      40,
    "low":         10,
    "none":        0,
}

# Tag → setter name (per routing sub-account)
TAG_TO_SETTER = {
    "cliente-adriana": "adriana",
    "cliente-claudia": "claudia",
    "cliente-edoardo": "edoardo",
    "cliente-filippo": "filippo",
    "cliente-laura":   "laura",
}
