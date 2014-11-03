function totalTableColumns(table) {
  if (table.rows.length > 1) {
    var sums = [];
    for (var i = 1; i < table.rows[0].cells.length; ++i) {
      sums[i] = 0;
    }

    for (var i = 1; i < table.rows.length; ++i) {
      for (var j = 1; j < table.rows[0].cells.length; ++j) {
        sums[j] += parseInt(table.rows[i].cells[j].innerHTML);
      }
    }

    return sums;
  }
}

function addTotalToTable() {
  var table = document.getElementById("summaryTable");
  var totals = totalTableColumns(table);
  var row = table.insertRow(table.rows.length);
  var label = row.insertCell(0);
  label.innerHTML = "Totals";
  for (var i = 1; i < totals.length; ++i) {
    var cell = row.insertCell(i);
    cell.innerHTML = totals[i].toString();
  }
}
