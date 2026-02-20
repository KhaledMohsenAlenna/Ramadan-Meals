function doPost(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var data = JSON.parse(e.postData.contents);
  var action = data.action;

  // 1. مسح كشف اليوم (يدوياً من الأزرار أو تلقائياً)
  if (action === "clear_day") {
    var lastRow = sheet.getLastRow();
    if (lastRow > 1) {
      sheet.deleteRows(2, lastRow - 1);
    }
    return ContentService.createTextOutput(JSON.stringify({"result": "success"})).setMimeType(ContentService.MimeType.JSON);
  }

  // 2. حذف طالب معين بالـ ID
  if (action === "delete_student") {
    var studentId = data.student_id;
    var values = sheet.getDataRange().getValues();
    for (var i = 1; i < values.length; i++) {
      if (values[i][3].toString() === studentId.toString()) {
        sheet.deleteRow(i + 1);
        return ContentService.createTextOutput(JSON.stringify({"result": "success"})).setMimeType(ContentService.MimeType.JSON);
      }
    }
    return ContentService.createTextOutput(JSON.stringify({"result": "not_found"})).setMimeType(ContentService.MimeType.JSON);
  }

  // 3. تأكيد الاستلام (تظليل الصف بالأخضر)
  if (action === "mark_received") {
    var studentId = data.student_id;
    var values = sheet.getDataRange().getValues();
    for (var i = 1; i < values.length; i++) {
      if (values[i][3].toString() === studentId.toString()) {
        sheet.getRange(i + 1, 1, 1, sheet.getLastColumn()).setBackground("#d9ead3"); // تظليل أخضر
        sheet.getRange(i + 1, 8).setValue("تم الاستلام ✅"); // تحديث الحالة
        return ContentService.createTextOutput(JSON.stringify({"result": "success"})).setMimeType(ContentService.MimeType.JSON);
      }
    }
    return ContentService.createTextOutput(JSON.stringify({"result": "not_found"})).setMimeType(ContentService.MimeType.JSON);
  }

  // 4. تسجيل حجز جديد (مع منع التكرار)
  var timestamp = new Date();
  var id = data.id;
  var email = data.email;
  var values = sheet.getDataRange().getValues();
  for (var i = 0; i < values.length; i++) {
    if (values[i][3].toString() === id.toString() || values[i][2].toString() === email.toString()) {
      return ContentService.createTextOutput(JSON.stringify({"result": "error", "message": "duplicate"})).setMimeType(ContentService.MimeType.JSON);
    }
  }
  sheet.appendRow([timestamp, data.name, email, id, data.location, data.gender, data.room]);
  return ContentService.createTextOutput(JSON.stringify({"result": "success"})).setMimeType(ContentService.MimeType.JSON);
}

// دالة المسح التلقائي - قم بضبط Trigger لها من الإعدادات لتعمل الساعة 12 بليل
function autoClearSheet() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var lastRow = sheet.getLastRow();
  if (lastRow > 1) {
    sheet.deleteRows(2, lastRow - 1);
  }
}
