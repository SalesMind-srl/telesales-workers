/**
 * Apps Script bridge — Marco Ferretti 2.0 Demo & Sales
 * Riceve post-call webhook ElevenLabs e tool-call salva_lead_qualificato.
 * Scrive nel foglio 1TJWURiz9bB4ZSqyBLcDkJd9YuSAeJbEW98CoauY7gC8 (Foglio1).
 *
 * Setup:
 *   1) Estensioni → Apps Script (questo file).
 *   2) Impostazioni progetto → Proprietà script: aggiungere
 *      WEBHOOK_SECRET = wsec_... (secret del webhook workspace ElevenLabs)
 *      (lasciare vuoto = nessuna verifica HMAC, solo per test)
 *   3) Esegui setupSheet() una volta per creare le intestazioni.
 *   4) Implementa → Nuova implementazione → Tipo: App web
 *      Esegui come: me. Chi ha accesso: chiunque (anche anonimo).
 *      Copia l'URL e incollalo nel webhook post-call ElevenLabs e nel
 *      tool salva_lead_qualificato dell'agente Marco Ferretti.
 */

var SHEET_ID = '1TJWURiz9bB4ZSqyBLcDkJd9YuSAeJbEW98CoauY7gC8';
var SHEET_NAME = 'Foglio1';

var HEADERS = [
  'Data',                // 1  A
  'Ora',                 // 2  B
  'Conversation ID',     // 3  C
  'Source',              // 4  D — post_call | tool_call
  'Nome contatto',       // 5  E
  'Ruolo',               // 6  F
  'Azienda',             // 7  G
  'Email',               // 8  H
  'Telefono',            // 9  I
  'Prodotto interesse',  // 10 J — AI Voice | HR | CRM | Scraping | Outreach | ...
  'Pain point',          // 11 K
  'Stato lead',          // 12 L — Caldo | Tiepido | Freddo | Appuntamento | Da richiamare
  'Appuntamento',        // 13 M — Sì/No
  'Note AI',             // 14 N — riassunto breve
  'Durata (s)',          // 15 O
  'Transcript link',     // 16 P
  'Riepilogo trascrizione' // 17 Q — testo riassunto
];

function authorizeAll() {
  // Esegui UNA VOLTA dall'editor per autorizzare: Spreadsheet + UrlFetch + MailApp.
  SpreadsheetApp.openById(SHEET_ID).getName();
  UrlFetchApp.fetch('https://api.elevenlabs.io/v1/voices', {
    headers: { 'xi-api-key': PropertiesService.getScriptProperties().getProperty('ELEVENLABS_API_KEY') || 'x' },
    muteHttpExceptions: true
  });
  // Richiede script.send_mail scope
  var q = MailApp.getRemainingDailyQuota();
  Logger.log('Authorized — mail quota residua: ' + q);
}

function setupSheet() {
  var ss = SpreadsheetApp.openById(SHEET_ID);
  var sh = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
  sh.clear();
  sh.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]);
  sh.getRange(1, 1, 1, HEADERS.length)
    .setFontWeight('bold')
    .setBackground('#1f1f1f')
    .setFontColor('#ffffff')
    .setHorizontalAlignment('center');
  sh.setFrozenRows(1);

  // Larghezze colonne ragionevoli
  var widths = [85, 60, 220, 90, 160, 140, 180, 220, 140, 140, 280, 130, 100, 320, 80, 260, 380];
  for (var i = 0; i < widths.length; i++) sh.setColumnWidth(i + 1, widths[i]);

  // Dropdown su "Stato lead"
  var statoRange = sh.getRange(2, 12, sh.getMaxRows() - 1, 1);
  var stati = ['Caldo', 'Tiepido', 'Freddo', 'Appuntamento', 'Da richiamare', 'Non interessato'];
  statoRange.setDataValidation(SpreadsheetApp.newDataValidation()
    .requireValueInList(stati, true).setAllowInvalid(false).build());

  // Dropdown su "Appuntamento"
  var appRange = sh.getRange(2, 13, sh.getMaxRows() - 1, 1);
  appRange.setDataValidation(SpreadsheetApp.newDataValidation()
    .requireValueInList(['Sì', 'No'], true).setAllowInvalid(false).build());

  SpreadsheetApp.flush();
}

// =============================================================
// Outbound call proxy — chiamami.html invoca questo endpoint
// con { action: "call", to_number: "+39..." } per far chiamare
// Marco Ferretti SIP all'utente che inserisce il numero.
// API key mai esposta al client.
// =============================================================

var ELEVENLABS_BASE   = 'https://api.elevenlabs.io';
var MARCO_SIP_AGENT   = 'agent_9201krn8z6ptevxsmx3g5e6vy69b';
var SIP_PHONE_ID      = 'phnum_1501kr3sx76sfxeap503jqy1m7j9';

function handleCallRequest_(payload) {
  var num = String(payload.to_number || '').replace(/[^\d+]/g, '');
  if (!/^\+\d{9,15}$/.test(num)) {
    return { ok: false, error: 'numero non valido' };
  }
  var apiKey = PropertiesService.getScriptProperties().getProperty('ELEVENLABS_API_KEY');
  if (!apiKey) return { ok: false, error: 'API key non configurata sul proxy' };

  var resp = UrlFetchApp.fetch(ELEVENLABS_BASE + '/v1/convai/sip-trunk/outbound-call', {
    method: 'post',
    contentType: 'application/json',
    headers: { 'xi-api-key': apiKey },
    payload: JSON.stringify({
      agent_id: MARCO_SIP_AGENT,
      agent_phone_number_id: SIP_PHONE_ID,
      to_number: num
    }),
    muteHttpExceptions: true
  });
  var code = resp.getResponseCode();
  var body = resp.getContentText();
  var data = {};
  try { data = JSON.parse(body); } catch (e) {}

  return { ok: code === 200 && data.success !== false, http: code, data: data };
}

function doPost(e) {
  try {
    var raw = e && e.postData && e.postData.contents ? e.postData.contents : '{}';
    var payload = JSON.parse(raw);

    // Outbound call request (chiamami.html)
    if (payload && payload.action === 'call' && payload.to_number) {
      var out = handleCallRequest_(payload);
      return ContentService.createTextOutput(JSON.stringify(out))
        .setMimeType(ContentService.MimeType.JSON);
    }

    var source = detectSource_(payload);

    if (source === 'post_call') {
      handlePostCall_(payload);
    } else if (source === 'tool_call') {
      handleToolCall_(payload);
    } else {
      handleGeneric_(payload);
    }

    return ContentService.createTextOutput(JSON.stringify({ ok: true, source: source }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ ok: false, error: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet() {
  return ContentService.createTextOutput('Marco Ferretti bridge — alive');
}

function detectSource_(p) {
  if (p && p.type && String(p.type).indexOf('post_call') === 0) return 'post_call';
  if (p && p.data && p.data.conversation_id && p.data.analysis) return 'post_call';
  if (p && (p.nome_azienda || p.tipo_interesse || p.stato_lead)) return 'tool_call';
  return 'generic';
}

function handlePostCall_(payload) {
  var d = payload.data || {};
  var convId = d.conversation_id || '';
  var dur = (d.metadata && d.metadata.call_duration_secs) || '';
  var startUnix = (d.metadata && d.metadata.start_time_unix_secs) || (payload.event_timestamp) || (Date.now() / 1000);
  var when = new Date(Number(startUnix) * 1000);

  var dc = (d.analysis && d.analysis.data_collection_results) || {};
  var v = function (k) {
    if (dc[k] && (dc[k].value !== undefined && dc[k].value !== null)) return String(dc[k].value);
    return '';
  };

  var summary = (d.analysis && d.analysis.transcript_summary) || '';
  var transcriptLink = convId ? ('https://elevenlabs.io/app/conversational-ai/history/' + convId) : '';

  // Default stato_lead: Caldo se ha lasciato email/telefono, altrimenti Da richiamare
  var hasContact = v('email_contatto') || v('telefono_diretto');
  var stato = hasContact ? 'Caldo' : 'Da richiamare';

  // Appuntamento: se nel summary o nelle note appare "appuntamento"
  var appuntamento = /appuntament|fissato|prenotat/i.test(summary + ' ' + v('note_ai')) ? 'Sì' : 'No';

  var row = [
    Utilities.formatDate(when, Session.getScriptTimeZone() || 'Europe/Rome', 'dd/MM/yyyy'),
    Utilities.formatDate(when, Session.getScriptTimeZone() || 'Europe/Rome', 'HH:mm'),
    convId,
    'post_call',
    v('nome_contatto'),
    v('ruolo_contatto'),
    v('azienda_nome'),
    v('email_contatto'),
    v('telefono_diretto'),
    v('prodotto_interesse') || guessProdotto_(summary),
    v('pain_point') || v('obiettivo_dichiarato'),
    stato,
    appuntamento,
    v('note_ai'),
    dur,
    transcriptLink,
    summary
  ];

  appendRow_(row);

  // Email notifica solo se chiamata POSITIVA (nome o email o telefono o appuntamento)
  var lead = {
    nome:       v('nome_contatto'),
    ruolo:      v('ruolo_contatto'),
    azienda:    v('azienda_nome'),
    email:      v('email_contatto'),
    telefono:   v('telefono_diretto'),
    prodotto:   v('prodotto_interesse') || guessProdotto_(summary),
    pain:       v('pain_point') || v('obiettivo_dichiarato'),
    note:       v('note_ai'),
    stato:      stato,
    appuntamento: appuntamento,
    data_app:   v('data_appuntamento') || v('data_appuntamento_iso8601'),
    durata:     dur,
    summary:    summary,
    transcript: transcriptLink
  };
  if (isPositive_(lead)) {
    sendNotifEmails_(lead);
  }
}

function isPositive_(lead) {
  if (!lead) return false;
  if (lead.nome) return true;
  if (lead.email) return true;
  if (lead.telefono) return true;
  if (lead.appuntamento === 'Sì' || lead.data_app) return true;
  if (lead.stato === 'Caldo' || lead.stato === 'Appuntamento') return true;
  return false;
}

function sendNotifEmails_(lead) {
  var TEAM_EMAIL = 'admintelesales@gmail.com';
  var FROM_NAME  = 'Marco Ferretti — Telesales.it';

  // 1) Email al lead (solo se ha lasciato email)
  if (lead.email) {
    try {
      var subjLead = 'Grazie per la chiacchierata — Telesales.it';
      var bodyLead =
        'Ciao' + (lead.nome ? ' ' + lead.nome.split(' ')[0] : '') + ',\n\n' +
        'sono Marco di Telesales.it. Grazie per i minuti che mi hai dedicato.\n\n' +
        'Riepilogo rapido di cosa ci siamo detti:\n' +
        (lead.summary ? lead.summary + '\n\n' : '') +
        (lead.prodotto ? 'Soluzione di cui abbiamo parlato: ' + lead.prodotto + '\n' : '') +
        (lead.appuntamento === 'Sì' || lead.data_app
          ? 'Appuntamento: ' + (lead.data_app || 'da confermare a breve') + '\n'
          : '') +
        '\nNiccolò Pratesi (il mio collega) ti ricontatta a breve per organizzare i 15 minuti di call su misura.\n\n' +
        'Se nel frattempo vuoi vedere cosa facciamo: https://telesales.it\n\n' +
        'A presto,\nMarco\n— Telesales.it';
      MailApp.sendEmail({
        to: lead.email,
        subject: subjLead,
        body: bodyLead,
        name: FROM_NAME,
        replyTo: TEAM_EMAIL
      });
    } catch (e) { /* fallback silenzioso, l'errore va nel log Apps Script */ }
  }

  // 2) Email al team — notifica nuovo lead positivo
  try {
    var subjTeam = '[Marco AI] Nuovo lead ' + (lead.stato || 'positivo') +
                   (lead.azienda ? ' — ' + lead.azienda : '') +
                   (lead.nome ? ' (' + lead.nome + ')' : '');
    var bodyTeam =
      'Marco Ferretti 2.0 ha appena gestito una chiamata positiva.\n\n' +
      '── DATI LEAD ──\n' +
      (lead.nome     ? 'Nome:     ' + lead.nome + '\n' : '') +
      (lead.ruolo    ? 'Ruolo:    ' + lead.ruolo + '\n' : '') +
      (lead.azienda  ? 'Azienda:  ' + lead.azienda + '\n' : '') +
      (lead.email    ? 'Email:    ' + lead.email + '\n' : '') +
      (lead.telefono ? 'Telefono: ' + lead.telefono + '\n' : '') +
      'Stato:    ' + (lead.stato || '-') + '\n' +
      'Prodotto: ' + (lead.prodotto || '-') + '\n' +
      'Appuntamento: ' + (lead.appuntamento || 'No') + (lead.data_app ? ' (' + lead.data_app + ')' : '') + '\n' +
      'Durata:   ' + (lead.durata || '-') + ' s\n' +
      (lead.pain ? '\nPain:\n' + lead.pain + '\n' : '') +
      (lead.note ? '\nNote AI:\n' + lead.note + '\n' : '') +
      (lead.summary ? '\nRiassunto chiamata:\n' + lead.summary + '\n' : '') +
      (lead.transcript ? '\nTrascrizione completa:\n' + lead.transcript + '\n' : '') +
      '\n── AZIONE ──\nNiccolò: organizza i 15 min con il lead. Foglio lead: https://docs.google.com/spreadsheets/d/' + SHEET_ID + '/edit\n';
    MailApp.sendEmail({
      to: TEAM_EMAIL,
      subject: subjTeam,
      body: bodyTeam,
      name: FROM_NAME
    });
  } catch (e) { /* idem */ }
}

function handleToolCall_(payload) {
  var when = new Date();
  var row = [
    Utilities.formatDate(when, Session.getScriptTimeZone() || 'Europe/Rome', 'dd/MM/yyyy'),
    Utilities.formatDate(when, Session.getScriptTimeZone() || 'Europe/Rome', 'HH:mm'),
    payload.conversation_id || '',
    'tool_call',
    payload.nome_contatto || '',
    payload.ruolo_contatto || '',
    payload.nome_azienda || '',
    payload.email_contatto || payload.email || '',
    payload.telefono_diretto || payload.telefono || '',
    payload.tipo_interesse || payload.prodotto_interesse || '',
    payload.pain_point || '',
    payload.stato_lead || 'Caldo',
    payload.appuntamento_preso ? 'Sì' : (payload.richiamata_programmata ? 'No' : ''),
    payload.note || payload.note_ai || '',
    payload.durata || '',
    '',
    ''
  ];
  appendRow_(row);

  // Email solo se positivo. Il post-call (a fine chiamata) inviera comunque la mail
  // definitiva: per evitare doppioni, qui mandiamo SOLO se c'è appuntamento (segnale forte real-time).
  if (payload.appuntamento_preso || payload.data_appuntamento) {
    var lead = {
      nome:       payload.nome_contatto || '',
      ruolo:      payload.ruolo_contatto || '',
      azienda:    payload.nome_azienda || '',
      email:      payload.email_contatto || payload.email || '',
      telefono:   payload.telefono_diretto || payload.telefono || '',
      prodotto:   payload.tipo_interesse || payload.prodotto_interesse || '',
      pain:       payload.pain_point || '',
      note:       payload.note || payload.note_ai || '',
      stato:      payload.stato_lead || 'Caldo',
      appuntamento: 'Sì',
      data_app:   payload.data_appuntamento || '',
      durata:     payload.durata || '',
      summary:    '',
      transcript: ''
    };
    if (isPositive_(lead)) sendNotifEmails_(lead);
  }
}

function handleGeneric_(payload) {
  var when = new Date();
  appendRow_([
    Utilities.formatDate(when, Session.getScriptTimeZone() || 'Europe/Rome', 'dd/MM/yyyy'),
    Utilities.formatDate(when, Session.getScriptTimeZone() || 'Europe/Rome', 'HH:mm'),
    '', 'generic', '', '', '', '', '', '', '', 'Da richiamare', '',
    JSON.stringify(payload).slice(0, 400), '', '', ''
  ]);
}

function guessProdotto_(text) {
  if (!text) return '';
  var t = String(text).toLowerCase();
  if (/ai voice|voice ai|chiamat|outbound|inbound/.test(t)) return 'AI Voice';
  if (/scraping|liste|prospect/.test(t)) return 'Scraping';
  if (/hr|candidat|selezion/.test(t)) return 'HR AI';
  if (/crm|follow.?up|pipeline/.test(t)) return 'CRM';
  if (/customer care|messaggi|whatsapp|inbox/.test(t)) return 'Outreach Omnicanale';
  if (/marketing|pubblicit|grafic/.test(t)) return 'Marketing AI';
  if (/bandi|investitor/.test(t)) return 'Bandi & Investitori';
  if (/eventi|invitati/.test(t)) return 'Agent Eventi';
  if (/digitale|corso|ebook/.test(t)) return 'Prodotti Digitali';
  return '';
}

function appendRow_(row) {
  var ss = SpreadsheetApp.openById(SHEET_ID);
  var sh = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
  if (sh.getLastRow() === 0) setupSheet();
  sh.appendRow(row);
}
