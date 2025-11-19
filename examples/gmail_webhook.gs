/**
 * Google Apps Script - Gmail Webhook 整合範例
 * 
 * 設定說明：
 * 1. 在 Google Apps Script 中建立新專案
 * 2. 複製此程式碼
 * 3. 設定觸發條件：當收到郵件時執行 processIncomingEmail
 * 4. 修改 API_ENDPOINT 為你的 Task Service URL
 */

// Task Service API 端點
const API_ENDPOINT = 'http://your-domain.com/api/webhook/gmail';

// 設定要處理的郵件標籤或條件
const TARGET_LABELS = ['財務', 'Bank', 'Credit Card'];
const TARGET_SENDERS = ['bank@example.com', 'creditcard@example.com'];

/**
 * 主要郵件處理函式
 * 當收到郵件時由觸發器自動執行
 */
function processIncomingEmail(e) {
  try {
    Logger.log('開始處理郵件...');
    
    // 取得最新的未讀郵件
    var threads = GmailApp.getInboxThreads(0, 10);
    
    threads.forEach(function(thread) {
      var messages = thread.getMessages();
      
      messages.forEach(function(message) {
        // 檢查是否為未讀郵件
        if (message.isUnread()) {
          processMessage(message);
        }
      });
    });
    
    Logger.log('郵件處理完成');
  } catch (error) {
    Logger.log('錯誤: ' + error.toString());
  }
}

/**
 * 處理單封郵件
 */
function processMessage(message) {
  var from = message.getFrom();
  var subject = message.getSubject();
  var date = message.getDate();
  
  Logger.log('處理郵件: ' + subject);
  
  // 檢查是否為目標寄件者
  if (!isTargetSender(from)) {
    Logger.log('跳過非目標寄件者: ' + from);
    return;
  }
  
  // 取得附件
  var attachments = message.getAttachments();
  
  if (attachments.length === 0) {
    Logger.log('沒有附件，跳過');
    return;
  }
  
  // 處理每個 PDF 附件
  attachments.forEach(function(attachment) {
    if (attachment.getContentType() === 'application/pdf') {
      processAttachment(attachment, from, subject, date);
    }
  });
  
  // 標記為已讀（可選）
  // message.markRead();
}

/**
 * 處理 PDF 附件
 */
function processAttachment(attachment, from, subject, date) {
  try {
    Logger.log('處理 PDF 附件: ' + attachment.getName());
    
    // 判斷文件類型
    var documentType = detectDocumentType(subject, from);
    
    // 準備要傳送的資料
    var formData = {
      'file': attachment.copyBlob().setName(attachment.getName()),
      'document_type': documentType,
      'sender': from,
      'subject': subject,
      'date': Utilities.formatDate(date, Session.getScriptTimeZone(), 'yyyy-MM-dd HH:mm:ss')
    };
    
    // 呼叫 Task Service API
    var options = {
      'method': 'post',
      'payload': formData,
      'muteHttpExceptions': true
    };
    
    var response = UrlFetchApp.fetch(API_ENDPOINT, options);
    var responseCode = response.getResponseCode();
    var responseText = response.getContentText();
    
    Logger.log('API 回應狀態: ' + responseCode);
    Logger.log('API 回應內容: ' + responseText);
    
    if (responseCode === 200) {
      var result = JSON.parse(responseText);
      handleSuccessResponse(result, documentType);
    } else {
      Logger.log('API 呼叫失敗: ' + responseText);
    }
    
  } catch (error) {
    Logger.log('處理附件時發生錯誤: ' + error.toString());
  }
}

/**
 * 判斷文件類型
 */
function detectDocumentType(subject, from) {
  subject = subject.toLowerCase();
  from = from.toLowerCase();
  
  // 銀行對帳單
  if (subject.includes('對帳單') || subject.includes('bank statement') || 
      subject.includes('月結單')) {
    return 'bank_statement';
  }
  
  // 信用卡帳單
  if (subject.includes('信用卡') || subject.includes('credit card') || 
      subject.includes('帳單') || subject.includes('繳款')) {
    return 'credit_card';
  }
  
  // 交易通知
  if (subject.includes('交易通知') || subject.includes('消費通知') || 
      subject.includes('transaction') || subject.includes('notification')) {
    return 'transaction_notice';
  }
  
  return 'unknown';
}

/**
 * 檢查是否為目標寄件者
 */
function isTargetSender(from) {
  // 如果沒有設定特定寄件者，則接受所有
  if (TARGET_SENDERS.length === 0) {
    return true;
  }
  
  from = from.toLowerCase();
  return TARGET_SENDERS.some(function(sender) {
    return from.includes(sender.toLowerCase());
  });
}

/**
 * 處理成功回應
 */
function handleSuccessResponse(result, documentType) {
  Logger.log('文件處理成功: ' + documentType);
  
  if (result.status === 'success' && result.data) {
    switch (documentType) {
      case 'bank_statement':
        updateGoogleSheets(result.data);
        break;
      case 'credit_card':
        updateGoogleCalendar(result.data);
        break;
      case 'transaction_notice':
        sendNotification(result.data);
        break;
    }
  }
}

/**
 * 更新 Google Sheets - 銀行對帳單
 */
function updateGoogleSheets(data) {
  try {
    // 請替換為你的 Google Sheets ID
    var sheetId = 'YOUR_GOOGLE_SHEETS_ID';
    var spreadsheet = SpreadsheetApp.openById(sheetId);
    var sheet = spreadsheet.getSheetByName('對帳單');
    
    // 如果工作表不存在，建立它
    if (!sheet) {
      sheet = spreadsheet.insertSheet('對帳單');
      // 建立標題列
      sheet.appendRow([
        '日期', '帳號', '期初餘額', '期末餘額', 
        '總存款', '總提款', '交易筆數', '處理時間'
      ]);
    }
    
    var summary = data.summary;
    
    // 新增資料列
    sheet.appendRow([
      summary.statement_period && summary.statement_period.dates ? 
        summary.statement_period.dates.join(' ~ ') : '',
      summary.account_number || '',
      summary.opening_balance || 0,
      summary.closing_balance || 0,
      summary.total_deposits || 0,
      summary.total_withdrawals || 0,
      summary.transaction_count || 0,
      data.processed_at || new Date().toISOString()
    ]);
    
    Logger.log('Google Sheets 更新成功');
  } catch (error) {
    Logger.log('更新 Google Sheets 時發生錯誤: ' + error.toString());
  }
}

/**
 * 更新 Google Calendar - 信用卡帳單
 */
function updateGoogleCalendar(data) {
  try {
    var calendar = CalendarApp.getDefaultCalendar();
    var summary = data.summary;
    
    if (summary.due_date) {
      // 解析到期日
      var dueDate = parseDate(summary.due_date);
      
      if (dueDate) {
        // 建立全天事件
        var title = '信用卡帳單到期 - ' + (summary.card_number || '');
        var description = 
          '應繳總額: $' + (summary.total_amount_due || 0).toLocaleString() + '\n' +
          '最低應繳: $' + (summary.minimum_payment || 0).toLocaleString() + '\n' +
          '本期消費: $' + (summary.new_charges || 0).toLocaleString();
        
        calendar.createAllDayEvent(title, dueDate, {
          description: description
        });
        
        // 建立提前 3 天的提醒事件
        var reminderDate = new Date(dueDate);
        reminderDate.setDate(reminderDate.getDate() - 3);
        
        calendar.createAllDayEvent(title + ' (提醒)', reminderDate, {
          description: description + '\n\n距離繳款截止日還有 3 天'
        });
        
        Logger.log('Google Calendar 更新成功');
      }
    }
  } catch (error) {
    Logger.log('更新 Google Calendar 時發生錯誤: ' + error.toString());
  }
}

/**
 * 發送通知 - 交易通知
 */
function sendNotification(data) {
  try {
    var summary = data.summary;
    var message = 
      '交易通知\n' +
      '日期: ' + (summary.transaction_date || '') + '\n' +
      '商家: ' + (summary.merchant || '') + '\n' +
      '金額: $' + (summary.amount || 0).toLocaleString() + '\n' +
      '類型: ' + (summary.transaction_type || '');
    
    // 可以使用 Gmail 發送通知
    // GmailApp.sendEmail('your-email@example.com', '交易通知', message);
    
    // 或使用其他通知方式（如 LINE Notify, Telegram 等）
    
    Logger.log('通知發送: ' + message);
  } catch (error) {
    Logger.log('發送通知時發生錯誤: ' + error.toString());
  }
}

/**
 * 解析日期字串
 */
function parseDate(dateString) {
  try {
    // 嘗試不同的日期格式
    dateString = dateString.replace(/年|月/g, '-').replace(/日/g, '');
    return new Date(dateString);
  } catch (error) {
    Logger.log('日期解析失敗: ' + dateString);
    return null;
  }
}

/**
 * 測試函式 - 手動執行以測試整合
 */
function testWebhook() {
  Logger.log('開始測試...');
  processIncomingEmail();
}

/**
 * 設定觸發器 - 執行一次以建立定時觸發器
 */
function setupTriggers() {
  // 移除現有觸發器
  var triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(function(trigger) {
    ScriptApp.deleteTrigger(trigger);
  });
  
  // 建立新的觸發器：每 5 分鐘檢查一次新郵件
  ScriptApp.newTrigger('processIncomingEmail')
    .timeBased()
    .everyMinutes(5)
    .create();
  
  Logger.log('觸發器設定完成');
}

