/*
#Copyright 2014 LinkedIn Corp.
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
* */
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
