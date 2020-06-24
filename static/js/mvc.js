function columnNamesFromTable(data) {
  // get the column names from the first row of data
  for (let k in data) {
    return Object.keys(data[k]);
  }
}

function joinTablesFor(table, spec) {
  return 'joins' in spec[table] ? spec[table]['joins'].map(j => j['join']) : [];
}

function setError(msg) {
  while (document.body.lastChild) {
    document.body.removeChild(document.body.lastChild);
  }

  let err = document.body.appendChild(document.createElement('div'));
  err.id = 'error';
  err.innerText = 'SHIT: ' + msg;
}

async function loadTable(table) {
// TODO: error handling
  const response = await fetch(
    '/editor/api/' + table,
    {
      method: 'GET',
      credentials: 'same-origin'
    }
  );

  if (!response.ok) {
    const msg = 'HTTP error, status = ' + response.status;
    setError(msg);
    console.log(response);
    throw new Error(msg);
  }

  return await response.json();
}

async function fetchTables(tables, table_cols, table_data) {
  await Promise.all(tables.map(async (table) => {
    let data = await loadTable(table);
    table_data[table] = data;
    table_cols[table] = columnNamesFromTable(data);
  }));
}

class Model extends EventTarget {
  constructor() {
    super();

    this.table_spec = {};
    this.table_data = {};
    this.table_cols = {};
  }

  deleteRow(table, id) {
    delete this.table_data[table][id];
    this.dispatchEvent(new CustomEvent('rowdeleted', {detail: id}));
  }

  updateRow(table, id, values) {
    this.table_data[table][id] = values;
    this.dispatchEvent(new CustomEvent('rowupdated', {detail: id}));
  }

  insertRow(table, id, values) {
    values['id'] = id;
    this.table_data[table][id] = values;
    this.dispatchEvent(new CustomEvent('rowinserted', {detail: id}));
  }
}

class PosthornModel extends Model {
  constructor() {
    super();

    // TODO: get the joins spec from the JSON API
    this.table_spec = {
      'award_types': {
        'readonly': ['id'],
        'joins': [
          {
            'join': 'groups',
            'on':   'group_id',
            'cols': ['name']
          }
        ]
      },
      'awards': {
        'readonly': ['id'],
        'hide': ['scribe_id', 'scroll_status_id', 'scroll_updated', 'scroll_comment'],
        'joins': [
          {
            'join': 'award_types',
            'on':   'type_id',
            'cols': ['name']
          },
          {
            'join': 'personae',
            'on':   'persona_id',
            'cols': ['name']
          },
          {
            'join': 'crowns',
            'on':   'crown_id',
            'cols': ['name']
          },
          {
            'join': 'events',
            'on':   'event_id',
            'cols': ['name']
          }
        ]
      },
      'crowns': {
        'readonly': ['id']
      },
      'events': {
        'readonly': ['id']
      },
      'groups': {
        'readonly': ['id']
      },
      'people': {
        'readonly': ['id'],
        'joins': [
          {
            'join': 'regions',
            'on':   'region_id',
            'cols': ['name']
          }
        ]
      },
      'personae': {
        'readonly': ['id'],
        'joins': [
          {
            'join': 'people',
            'on':   'person_id',
            'cols': ['surname', 'forename']
          }
        ]
      },
      'regions': {
        'readonly': ['id']
      },
      'reigns': {
        'readonly': ['id']
      },
      'scribes': {
        'readonly': ['id']
      },
      'scroll_status': {
        'readonly': ['id']
      }
    };
  }
}

class SignetModel extends Model {
  constructor() {
    super();

    // TODO: get the joins spec from the JSON API
    this.table_spec = {
      'awards': {
        'readonly': ['id', 'type_id', 'persona_id', 'crown_id', 'event_id', 'date', 'award_types.name', 'personae.name', 'crowns.name', 'events.name'],
        'hide': ['id', 'type_id', 'persona_id', 'crown_id', 'event_id'],
        'insert': false,
        'joins': [
          {
            'join': 'scribes',
            'on':   'scribe_id',
            'cols': ['name']
          },
          {
            'join': 'award_types',
            'on':   'type_id',
            'cols': ['name']
          },
          {
            'join': 'personae',
            'on':   'persona_id',
            'cols': ['name']
          },
          {
            'join': 'crowns',
            'on':   'crown_id',
            'cols': ['name']
          },
          {
            'join': 'events',
            'on':   'event_id',
            'cols': ['name']
          }
        ]
      },
      'scribes': {
        'readonly': ['id']
      },
      'scroll_status': {
        'readonly': ['id']
      }
    };
  }
}

function rowId(id) {
  return 'row_' + id;
}

function dataListId(table, column) {
  return 'dl_' + table + '.' + column;
}

function makeDataLists(jtabs, table_data) {
  // create datalists
  for (const j of jtabs) {
    for (const jcol of j['cols']) {
      let dl = document.body.appendChild(document.createElement('datalist'));
      dl.id = dataListId(j['join'], jcol);
      const join_data = table_data[j['join']];
      for (const id in join_data) {
        let opt = dl.appendChild(document.createElement('option'));
        opt.value = join_data[id][jcol];
        opt.setAttribute('data-id', id);
      }
    }
  }
}

function makeHeaders(columnNames, spec, jtabs, thead) {
  let thead_row = thead.insertRow();
  thead_row.setAttribute('data-sort-method', 'thead');

  // headers for table columns
  for (let col of columnNames) {
    if ('hide' in spec && spec['hide'].includes(col)) {
      continue;
    }

    let th = thead_row.appendChild(document.createElement('th'));
    th.innerText = col;

     if (col === 'id') {
      // id column is default sort column
      th.setAttribute('data-sort-default', '');
    }
  }

  // headers for join columns
  for (let j of jtabs) {
    for (let jcol of j['cols']) {
      let th = thead_row.appendChild(document.createElement('th'));
      th.innerText = j['join'] + '.' + jcol;
    }
  }
}

function insertCellId(col) {
  return 'row_insert_' + col;
}

function insertJoinCellId(table, col) {
  return 'row_insert_' + table + '.' + col;
}

function editCellId(col) {
  return 'row_edit_' + col;
}

function editJoinCellId(table, col) {
  return 'row_edit_' + table + '.' + col;
}

function isEditRowValid() {
  for (let i of document.getElementsByClassName('edit_row input')) {
    if (!i.checkValidity()) {
      return false;
    }
  }
  return true;
}

function isEditRowChanged() {
  for (let i of document.getElementsByClassName('edit_row input')) {
    if (i.value !== i.getAttribute('data-original_value')) {
      return true;
    }
  }
  return false;
}

function isInsertRowValid() {
  for (let i of document.getElementsByClassName('insert_row input')) {
    if (!i.checkValidity()) {
      return false;
    }
  }
  return true;
}

function isInsertRowEmpty() {
  for (let i of document.getElementsByClassName('insert_row input')) {
    if (i.value !== '') {
      return false;
    }
  }
  return true;
}

function updateButtons() {
  if (isInsertRowEmpty()) {
    // enable edit and delete buttons for existing rows
    for (let b of document.getElementsByClassName('data_row button')) {
      b.classList.remove('disabled');
    }

    // disable commit and delete buttons for insert row
    for (let b of document.getElementsByClassName('insert_row button')) {
      b.classList.add('disabled');
    }
  }
  else {
    // disable edit and delete buttons for existing rows
    for (let b of document.getElementsByClassName('data_row button')) {
      b.classList.add('disabled');
    }

    // enable delete button for insert row
    for (let b of document.getElementsByClassName('insert_row button delete')) {
      b.classList.remove('disabled');
    }

    if (isInsertRowValid()) {
      for (let b of document.getElementsByClassName('insert_row button add')) {
        b.classList.remove('disabled');
      }
    }
    else {
      for (let b of document.getElementsByClassName('insert_row button add')) {
        b.classList.add('disabled');
      }
    }
  }
}

function valuesFromInsertRow() {
  let values = {};
  for (let i of document.getElementsByClassName('insert_row input')) {
    const col = i.getAttribute('data-input_for');
    if (col) {
      values[col] = i.value;
    }
  }
  return values;
}

function valuesFromEditRow() {
  let values = {};
  for (let i of document.getElementsByClassName('edit_row input')) {
    const col = i.getAttribute('data-input_for');
    if (col) {
      values[col] = i.value;
    }
  }
  return values;
}

function isEditing() {
  for (let i of document.getElementsByClassName('edit_row')) {
    return true;
  }
  return false;
}

function updateButtonsEdit() {
  for (let b of document.getElementsByClassName('insert_row button ')) {
    b.classList.add('disabled');
  }

  if (isEditing()) {
    for (let b of document.getElementsByClassName('insert_row input')) {
      b.disabled = true;
    }

    for (let b of document.getElementsByClassName('data_row button')) {
      b.classList.add('disabled');
    }

    if (isEditRowValid() && isEditRowChanged()) {
      for (let b of document.getElementsByClassName('edit_row button update')) {
        b.classList.remove('disabled');
      }
    }
    else {
      for (let b of document.getElementsByClassName('edit_row button update')) {
        b.classList.add('disabled');
      }
    }
  }
  else {
    for (let b of document.getElementsByClassName('insert_row input')) {
      b.disabled = false;
    }

    for (let b of document.getElementsByClassName('data_row button')) {
      b.classList.remove('disabled');
    }
  }
}

function clearInputRow() {
  for (let i of document.getElementsByClassName('insert_row input')) {
    i.value = '';
    i.setCustomValidity('');
  }
  updateButtons();
}

function clearTable() {
  let table = document.getElementById('the_table');
  let thead = document.getElementById('the_table_header');
  let tbody = document.getElementById('the_table_body');

  let new_thead = document.createElement('thead');
  table.replaceChild(new_thead, thead);
  new_thead.id = thead.id;

  let new_tbody = document.createElement('tbody');
  table.replaceChild(new_tbody, tbody);
  new_tbody.id = tbody.id;
}

class View {
  constructor(model) {
    this.model = model;
    this.controller = null;

    this.model.addEventListener('rowdeleted', e => this.removeDataRow(e.detail));
    this.model.addEventListener('rowinserted', e => this.insertDataRow(e.detail));
    this.model.addEventListener('rowupdated', e => this.updateDataRow(e.detail));
  }

  makeTable(table) {
    console.log("Rendering " + table);

    clearTable();

    const model = this.model;

    const cols = model.table_cols[table];
    const spec = model.table_spec[table];
    const data = model.table_data[table];
    const jtabs = 'joins' in spec ? spec['joins'] : [];

    let thead = document.getElementById('the_table_header');
    let tbody = document.getElementById('the_table_body');

    makeDataLists(jtabs, model.table_data);
    makeHeaders(cols, spec, jtabs, thead);
    this.makeInsertRow(cols, spec, jtabs, thead);

    for (let id in data) {
      this.makeDataRow(table, cols, spec, jtabs, data[id], model.table_data, tbody, -1);
    }

    new Tablesort(document.getElementById('the_table'));
  }

  makeDataRow(tname, cols, spec, jtabs, row, table_data, tbody, index) {
    const id = row['id'];

    // table data
    let tr = tbody.insertRow(index);
    tr.id = rowId(id);

    for (let c of cols) {
      if ('hide' in spec && spec['hide'].includes(c)) {
        continue;
      }

      let td = tr.insertCell();
      td.innerText = row[c];
    }

    // join data
    for (let j of jtabs) {
      const join_row = table_data[j['join']][row[j['on']]];
      for (let jcol of j['cols']) {
        let td = tr.insertCell();
        td.innerText = join_row[jcol];
      }
    }

    // edit button
    let edit = tr.insertCell();
    edit.classList.add('data_row', 'button', 'edit');
    edit.innerText = '✎';
    edit.addEventListener('click', () => {
      if (!edit.classList.contains('disabled')) {
        const index = tr.rowIndex-2;
        this.removeDataRow(id);
        this.makeEditableRow(tname, cols, spec, jtabs, row, table_data, tbody, index);
      }
    });

    // delete button
    let del = tr.insertCell();
    del.classList.add('data_row', 'button', 'delete');
    del.innerText = '✖';
    del.addEventListener('click', () => del.classList.contains('disabled') || this.controller.deleteRow.bind(this.controller)(id));
  }

  removeDataRow(id) {
    let tr = document.getElementById(rowId(id));
    tr.parentNode.removeChild(tr);
  }

  removeEditableRow(id) {
    let tr = document.getElementById(rowId(id));
    tr.parentNode.removeChild(tr);
  }

  insertDataRow(id) {
    const table = this.controller.table;
    const table_data = this.model.table_data;
    const row = table_data[table][id];

    const cols = this.model.table_cols[table];
    const spec = this.model.table_spec[table];
    const jtabs = 'joins' in spec ? spec['joins'] : [];

    let tbody = document.getElementById('the_table_body');

    this.makeDataRow(table, cols, spec, jtabs, row, table_data, tbody, 0);
  }

  updateDataRow(id) {
    let tr = document.getElementById(rowId(id));
    const index = tr.rowIndex - 2;
    tr.parentNode.removeChild(tr);

    const table = this.controller.table;
    const table_data = this.model.table_data;
    const row = table_data[table][id];

    const cols = this.model.table_cols[table];
    const spec = this.model.table_spec[table];
    const jtabs = 'joins' in spec ? spec['joins'] : [];

    let tbody = document.getElementById('the_table_body');

    this.makeDataRow(table, cols, spec, jtabs, row, table_data, tbody, index);

    updateButtonsEdit();
  }

  makeInsertRow(cols, spec, jtabs, thead) {
    let insert_row = thead.insertRow();
    insert_row.id = 'row_insert';

    if ('insert' in spec && !spec['insert']) {
      return;
    }

    // inputs for table columns
    for (let col of cols) {
      if ('hide' in spec && spec['hide'].includes(col)) {
        // column is invisible
        continue;
      }

      let td = insert_row.insertCell();

      if ('readonly' in spec && spec['readonly'].includes(col)) {
        // column is not settable
        continue;
      }

  // TODO: add validation for direct input into foreign key columns
      let input = td.appendChild(document.createElement('input'));
      input.type = 'text';
      input.id = insertCellId(col);
      input.setAttribute('data-input_for', col);
      input.classList.add('insert_row', 'input');
      input.addEventListener('input', updateButtons);
    }

    // inputs for join columns
    for (let j of jtabs) {
      for (let jcol of j['cols']) {
        // create record inputs
        let td = insert_row.insertCell();

        const jcolname = j['join'] + '.' + jcol;
        if ('readonly' in spec && spec['readonly'].includes(jcolname)) {
          // column is not settable
          continue;
        }

        let input = td.appendChild(document.createElement('input'));
        input.type = 'text';
        input.autocomplete = 'on';
        input.id = insertJoinCellId(j['join'], jcol);
        input.classList.add('insert_row', 'input');
        input.setAttribute('list', dataListId(j['join'], jcol));
        input.addEventListener('input', function() {
          let on_input = document.getElementById(insertCellId(j['on']));
          let dl = this.list;
  // TODO: binary search
          for (let o of dl.options) {
            if (o.value === this.value) {
              on_input.value = o.getAttribute('data-id');
              this.setCustomValidity('');
              updateButtons();
              return;
            }
          }
          on_input.value = '';
          this.setCustomValidity('FUUUUUUCK!');
          updateButtons();
        });
      }
    }

    // commit button
    let commit = insert_row.insertCell();
    commit.classList.add('insert_row', 'button', 'add', 'disabled');
    commit.innerText = '✓';
    commit.addEventListener('click', () => {
      if (commit.classList.contains('disabled')) {
        return;
      }
      const values = valuesFromInsertRow();
      clearInputRow();

      for (let t in ['readonly', 'hide']) {
        if (t in spec) {
          for (let s of spec[t]) {
            if (s != 'id' && s in values) {
              delete values[s];
            }
          }
        }
      }

      this.controller.insertRow.bind(this.controller)(values);
    });

    // delete button
    let del = insert_row.insertCell();
    del.classList.add('insert_row', 'button', 'delete', 'disabled');
    del.innerText = '✖';
    del.addEventListener('click', () => del.classList.contains('disabled') || clearInputRow());
  }

  makeEditableRow(tname, cols, spec, jtabs, row, table_data, tbody, index) {
    const id = row['id'];

    // table data
    let tr = tbody.insertRow(index);
    tr.id = rowId(id);

    // table columns
    for (let col of cols) {
      if ('hide' in spec && spec['hide'].includes(col)) {
        continue;
      }

      let td = tr.insertCell();

      if ('readonly' in spec && spec['readonly'].includes(col)) {
        // column is not settable
        td.innerText = row[col];
        continue;
      }

      let input = td.appendChild(document.createElement('input'));
      input.type = 'text';
      input.value = row[col];
      input.setAttribute('data-original_value', input.value);
      input.id = editCellId(col);
      input.setAttribute('data-input_for', col);
      input.classList.add('edit_row', 'input');
      input.addEventListener('input', updateButtonsEdit);
    }

    // join columns
    for (let j of jtabs) {
      const join_row = table_data[j['join']][row[j['on']]];
      for (let jcol of j['cols']) {
        let td = tr.insertCell();

        const jcolname = j['join'] + '.' + jcol;
        if ('readonly' in spec && spec['readonly'].includes(jcolname)) {
          // column is not settable
          td.innerText = join_row[jcol];
          continue;
        }

        let input = td.appendChild(document.createElement('input'));
        input.type = 'text';
        input.value = join_row[jcol];
        input.setAttribute('data-original_value', input.value);
        input.autocomplete = 'on';
        input.id = editJoinCellId(j['join'], jcol);
        input.classList.add('edit_row', 'input');
        input.setAttribute('list', dataListId(j['join'], jcol));
        input.addEventListener('input', function() {
          let on_input = document.getElementById(editCellId(j['on']));
          let dl = this.list;
  // TODO: binary search
          for (let o of dl.options) {
            if (o.value === this.value) {
              on_input.value = o.getAttribute('data-id');
              this.setCustomValidity('');
              updateButtonsEdit();
              return;
            }
          }
          on_input.value = '';
          this.setCustomValidity('FUUUUUUCK!');
          updateButtonsEdit();
        });
      }
    }

    // update button
    let update = tr.insertCell();
    update.innerText = '✓';
    update.classList.add('edit_row', 'button', 'update');
    update.addEventListener('click', () => {
      if (!update.classList.contains('disabled')) {
        const values = valuesFromEditRow();

        for (let t in ['readonly', 'hide']) {
          if (t in spec) {
            for (let s of spec[t]) {
              if (s != 'id' && s in values) {
                delete values[s];
              }
            }
          }
        }

        this.controller.updateRow.bind(this.controller)(id, values);
      }
    });

    // undo button
    let undo = tr.insertCell();
    undo.innerText = '⮌';
    undo.classList.add('edit_row', 'button', 'undo');
    undo.addEventListener('click', () => {
      this.removeEditableRow(id);
      this.makeDataRow(tname, cols, spec, jtabs, row, table_data, tbody, index);
      updateButtonsEdit();
    });

    updateButtonsEdit();
  }
}

class Controller {
  constructor(model, view) {
    this.model = model;
    this.view = view;
    this.table = null;

    this.view.controller = this;
  }

  async showTable(table) {
    console.log("Going to show " + table);

    document.body.classList.add('wait');

    this.table = table;
    const model = this.model;

    // determine which tables we need for display
    const tables = [table, ...joinTablesFor(table, model.table_spec)];
    const missing_tables = tables.filter(t => !(t in model.table_data));

    // fetch data for any tables we don't have yet
    if (missing_tables.length) {
      await fetchTables(missing_tables, model.table_cols, model.table_data);
      console.log("Loaded " + missing_tables);
    }

    // tell the view to show the table
    this.view.makeTable(this.table);

    document.body.classList.remove('wait');
  }

  async deleteRow(id) {
    console.log("Going to delete row " + id);

    const url = '/editor/api/' + this.table + '/' + id;
    const response = await fetch(
      url,
      {
        method: 'DELETE',
        credentials: 'same-origin'
      }
    );

    if (!response.ok) {
      const msg = 'HTTP error, status = ' + response.status;
      setError(msg);
      throw new Error(msg);
    }

    // update model
    this.model.deleteRow(this.table, id);
  }

  async insertRow(row) {
    console.log("Going to insert row ", row);

    const params = {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(row)
    };

    const response = await fetch('/editor/api/' + this.table, params);

    if (!response.ok) {
// TODO: handle error better
      const msg = 'HTTP error, status = ' + response.status;
      setError(msg);
      throw new Error(msg);
    }

    const json = await response.json();
    const id = json['id'];

    // update model
    this.model.insertRow(this.table, id, row);
  }

  async updateRow(id, row) {
    console.log("Going to update row ", id, row);

    const params = {
      method: 'PATCH',
      credentials: 'same-origin',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(row)
    };

    const response = await fetch('/editor/api/' + this.table + '/' + id, params);

    if (!response.ok) {
      const msg = 'HTTP error, status = ' + response.status;
      setError(msg);
      throw new Error(msg);
    }

    // update model
    row['id'] = id;
    this.model.updateRow(this.table, id, row);
  }
}
