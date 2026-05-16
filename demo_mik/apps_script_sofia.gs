/**
 * Sofia ↔ Google Sheet bridge per campagna Mik Cosentino.
 *
 * - Menu "Sofia AI" → "Lancia chiamate non ancora fatte" (legge tab "Lead Demo (50)")
 * - Endpoint webhook doPost: riceve post-call event ElevenLabs e aggiorna riga del lead.
 *
 * Configurazione (Project Settings → Script properties):
 *   ELEVENLABS_API_KEY      = sk_...
 *   ELEVENLABS_AGENT_ID     = agent_8001krjx3v8vfvktyc1z3xsqv0m8
 *   ELEVENLABS_PHONE_ID     = phnum_1501kr3sx76sfxeap503jqy1m7j9
 */

const SHEET_TAB = 'lead_demo_team_telesales'; // tab principale 50 lead
const COLS = {
  id: 'A', data_iscrizione: 'B', nome: 'C', cognome: 'D', email: 'E', telefono: 'F',
  cosa_fai_per_vivere: 'G', obiettivo_3_6_mesi: 'H', perche_importante: 'I', cosa_ostacola: 'J',
  consenso_marketing: 'K', consenso_whatsapp: 'L', ultimo_contatto: 'M', note_storiche: 'N',
  // colonne di output (popolate da webhook ElevenLabs)
  status: 'O',
  esito_ai: 'P', appuntamento_fissato: 'Q', data_appuntamento: 'R',
  obiezione_principale: 'S', opt_out: 'T', note_ai: 'U',
  email_confermata: 'V', telefono_confermato: 'W',
  audio_url: 'X', conversation_id: 'Y', ts_chiamata: 'Z',
};

const OUTPUT_HEADERS = [
  'status', 'esito_ai', 'appuntamento_fissato', 'data_appuntamento',
  'obiezione_principale', 'opt_out', 'note_ai',
  'email_confermata', 'telefono_confermato',
  'audio_url', 'conversation_id', 'ts_chiamata'
];

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('Sofia AI')
    .addItem('Lancia chiamate non ancora fatte', 'lanciaChiamate')
    .addItem('Setup colonne output', 'setupOutputColumns')
    .addItem('Reset stato chiamate (azzera output)', 'resetOutputColumns')
    .addToUi();
}

function setupOutputColumns() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sh = ss.getSheetByName(SHEET_TAB) || ss.getActiveSheet();
  const lastCol = sh.getLastColumn();
  const headerRow = sh.getRange(1, 1, 1, Math.max(lastCol, 14)).getValues()[0];
  // aggiungo header output se non già presenti
  const existingHeaders = new Set(headerRow.map(h => String(h).trim()));
  let nextCol = lastCol + 1;
  const toAdd = [];
  for (const h of OUTPUT_HEADERS) {
    if (!existingHeaders.has(h)) {
      toAdd.push(h);
    }
  }
  if (toAdd.length === 0) {
    SpreadsheetApp.getUi().alert('Colonne output gia presenti.');
    return;
  }
  sh.getRange(1, nextCol, 1, toAdd.length).setValues([toAdd]);
  // stile header
  const range = sh.getRange(1, nextCol, 1, toAdd.length);
  range.setFontWeight('bold').setFontColor('#FFFFFF').setBackground('#374151');
  SpreadsheetApp.getUi().alert('Aggiunte ' + toAdd.length + ' colonne output: ' + toAdd.join(', '));
}

function resetOutputColumns() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sh = ss.getSheetByName(SHEET_TAB) || ss.getActiveSheet();
  const lastRow = sh.getLastRow();
  if (lastRow < 2) return;
  // cancello dalla colonna O in poi (output)
  const startCol = 15; // O
  const lastCol = sh.getLastColumn();
  if (lastCol >= startCol) {
    sh.getRange(2, startCol, lastRow - 1, lastCol - startCol + 1).clearContent();
  }
  SpreadsheetApp.getUi().alert('Output azzerati.');
}

function lanciaChiamate() {
  const props = PropertiesService.getScriptProperties();
  const API_KEY = props.getProperty('ELEVENLABS_API_KEY');
  const AGENT_ID = props.getProperty('ELEVENLABS_AGENT_ID');
  const PHONE_ID = props.getProperty('ELEVENLABS_PHONE_ID');
  if (!API_KEY || !AGENT_ID || !PHONE_ID) {
    SpreadsheetApp.getUi().alert('Script properties mancanti: ELEVENLABS_API_KEY, ELEVENLABS_AGENT_ID, ELEVENLABS_PHONE_ID.');
    return;
  }

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sh = ss.getSheetByName(SHEET_TAB) || ss.getActiveSheet();
  const lastRow = sh.getLastRow();
  if (lastRow < 2) {
    SpreadsheetApp.getUi().alert('Nessuna riga da chiamare.');
    return;
  }

  // assicuro le colonne output
  setupOutputColumnsSilently_(sh);
  const headers = sh.getRange(1, 1, 1, sh.getLastColumn()).getValues()[0];
  const colIdx = {};
  headers.forEach((h, i) => colIdx[String(h).trim()] = i);

  const rows = sh.getRange(2, 1, lastRow - 1, sh.getLastColumn()).getValues();
  const recipients = [];
  const rowsLanced = [];

  rows.forEach((r, i) => {
    const status = r[colIdx['status']] || '';
    if (status === 'CHIAMATO' || status === 'IN_CORSO') return;
    const tel = String(r[colIdx['telefono']] || '').trim();
    if (!tel || tel.indexOf('+') !== 0) return;
    const consensoMarketing = String(r[colIdx['consenso_marketing']] || '').toLowerCase();
    const optOut = String(r[colIdx['opt_out']] || '').toLowerCase();
    if (consensoMarketing !== 'si' || optOut === 'true' || optOut === 'si') return;

    recipients.push({
      phone_number: tel,
      conversation_initiation_client_data: {
        dynamic_variables: {
          nome: r[colIdx['nome']] || '',
          cognome: r[colIdx['cognome']] || '',
          email: r[colIdx['email']] || '',
          telefono: tel,
          data_iscrizione: r[colIdx['data_iscrizione']] || '',
          cosa_fai_per_vivere: r[colIdx['cosa_fai_per_vivere']] || '',
          obiettivo_3_6_mesi: r[colIdx['obiettivo_3_6_mesi']] || '',
          perche_importante: r[colIdx['perche_importante']] || '',
          cosa_ostacola: r[colIdx['cosa_ostacola']] || '',
          // metadata custom — utili per il webhook return
          lead_id: r[colIdx['id']] || ''
        }
      }
    });
    rowsLanced.push(i + 2); // riga reale
  });

  if (recipients.length === 0) {
    SpreadsheetApp.getUi().alert('Nessuna riga eleggibile (telefono mancante, consenso = no, gia chiamato o opt-out).');
    return;
  }

  // POST a ElevenLabs batch
  const payload = {
    call_name: 'Sofia Mik batch ' + new Date().toISOString(),
    agent_id: AGENT_ID,
    agent_phone_number_id: PHONE_ID,
    recipients: recipients
  };
  const resp = UrlFetchApp.fetch('https://api.elevenlabs.io/v1/convai/batch-calling/submit', {
    method: 'post',
    contentType: 'application/json',
    headers: { 'xi-api-key': API_KEY },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  });
  const code = resp.getResponseCode();
  const txt = resp.getContentText();
  if (code < 200 || code >= 300) {
    SpreadsheetApp.getUi().alert('Errore ElevenLabs (' + code + '):\n' + txt.substring(0, 500));
    return;
  }
  const body = JSON.parse(txt);
  const batchId = body.id || body.batch_id || '';
  const ts = new Date();

  // marco le righe come IN_CORSO
  rowsLanced.forEach(r => {
    sh.getRange(r, colIdx['status'] + 1).setValue('IN_CORSO');
    sh.getRange(r, colIdx['ts_chiamata'] + 1).setValue(ts);
  });

  SpreadsheetApp.getUi().alert('Batch lanciato!\n\nRecipients: ' + recipients.length + '\nBatch ID: ' + batchId);
}

function setupOutputColumnsSilently_(sh) {
  const lastCol = sh.getLastColumn();
  const headerRow = sh.getRange(1, 1, 1, lastCol).getValues()[0];
  const existingHeaders = new Set(headerRow.map(h => String(h).trim()));
  const toAdd = OUTPUT_HEADERS.filter(h => !existingHeaders.has(h));
  if (toAdd.length === 0) return;
  const startCol = lastCol + 1;
  sh.getRange(1, startCol, 1, toAdd.length).setValues([toAdd]);
  sh.getRange(1, startCol, 1, toAdd.length)
    .setFontWeight('bold').setFontColor('#FFFFFF').setBackground('#374151');
}

/**
 * Webhook endpoint chiamato da ElevenLabs post-call.
 * Deploy come Web App (Anyone) → URL da inserire nelle agent settings (post call webhook).
 *
 * Payload atteso (ElevenLabs Conversational AI post-call webhook):
 * {
 *   "type": "post_call_transcription",
 *   "event_timestamp": ...,
 *   "data": {
 *     "agent_id": "...",
 *     "conversation_id": "...",
 *     "status": "done"|"failed",
 *     "analysis": {
 *       "data_collection_results": { ... },
 *       "transcript_summary": "..."
 *     },
 *     "conversation_initiation_client_data": {
 *       "dynamic_variables": { "lead_id": "MIK-DEMO-001", ... }
 *     },
 *     "metadata": { "phone_call": { "external_number": "+39..." }, ... }
 *   }
 * }
 */
function doPost(e) {
  try {
    const payload = JSON.parse(e.postData.contents);
    const data = payload.data || payload;
    const conv_id = data.conversation_id || data.conversationId || '';
    const init = data.conversation_initiation_client_data || {};
    const dyn = init.dynamic_variables || {};
    const lead_id = dyn.lead_id || '';
    const tel = (data.metadata && data.metadata.phone_call && data.metadata.phone_call.external_number) || dyn.telefono || '';
    const analysis = data.analysis || {};
    const dc = analysis.data_collection_results || {};

    // helper: estrai value da data_collection_results (puo' essere stringa o oggetto {value, rationale})
    function val(k) {
      const v = dc[k];
      if (v === null || v === undefined) return '';
      if (typeof v === 'object') return v.value !== undefined ? v.value : JSON.stringify(v);
      return v;
    }

    const summary = analysis.transcript_summary || '';
    const audio_url = data.metadata && data.metadata.audio_url || '';
    const call_status = data.status || '';

    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sh = ss.getSheetByName(SHEET_TAB) || ss.getActiveSheet();
    const lastRow = sh.getLastRow();
    const headers = sh.getRange(1, 1, 1, sh.getLastColumn()).getValues()[0];
    const idx = {};
    headers.forEach((h, i) => idx[String(h).trim()] = i);

    // trova la riga del lead per id o telefono
    let targetRow = -1;
    if (lead_id) {
      const ids = sh.getRange(2, idx['id'] + 1, lastRow - 1, 1).getValues();
      for (let i = 0; i < ids.length; i++) {
        if (String(ids[i][0]).trim() === String(lead_id).trim()) { targetRow = i + 2; break; }
      }
    }
    if (targetRow < 0 && tel) {
      const phones = sh.getRange(2, idx['telefono'] + 1, lastRow - 1, 1).getValues();
      for (let i = 0; i < phones.length; i++) {
        if (String(phones[i][0]).replace(/\s/g, '') === String(tel).replace(/\s/g, '')) { targetRow = i + 2; break; }
      }
    }
    if (targetRow < 0) {
      return ContentService.createTextOutput(JSON.stringify({ok: false, error: 'lead non trovato', lead_id: lead_id, tel: tel}))
        .setMimeType(ContentService.MimeType.JSON);
    }

    // Scrivi output
    const updates = [
      ['status', 'CHIAMATO'],
      ['esito_ai', val('interest_level')],
      ['appuntamento_fissato', val('appuntamento_fissato')],
      ['data_appuntamento', val('data_appuntamento')],
      ['obiezione_principale', val('obiezione_principale')],
      ['opt_out', val('opt_out_richiesto')],
      ['note_ai', val('note_ai') || summary],
      ['email_confermata', val('email_confermata')],
      ['telefono_confermato', val('telefono_confermato')],
      ['audio_url', audio_url],
      ['conversation_id', conv_id],
      ['ts_chiamata', new Date()]
    ];
    updates.forEach(([k, v]) => {
      if (idx[k] !== undefined) sh.getRange(targetRow, idx[k] + 1).setValue(v);
    });

    return ContentService.createTextOutput(JSON.stringify({ok: true, row: targetRow}))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ok: false, error: String(err)}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet() {
  return ContentService.createTextOutput('Sofia ↔ Sheet bridge attivo.');
}
