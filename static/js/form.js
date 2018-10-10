var form = document.getElementsByTagName('form')[0];

var reset = document.getElementById('reset');

var persona = document.getElementById('persona');
var forename = document.getElementById('forename');
var surname = document.getElementById('surname');
var begin = document.getElementById('begin');
var end = document.getElementById('end');
var crown = document.getElementById('crown');
var award = document.getElementById('award');

var inputs = [persona, forename, surname, begin, end, crown, award];

var non_persona = inputs.filter(x => x != persona);
var with_persona = [];
var non_forename = inputs.filter(x => x != forename && x != surname);
var with_forename = [surname]
var non_surname = non_forename;
var with_surname = [forename];
var non_begin = inputs.filter(x => x != begin && x != end);
var with_begin = [end];
var non_end = non_begin;
var with_end = [begin];
var non_crown = inputs.filter(x => x != crown);
var with_crown = [];
var non_award = inputs.filter(x => x != award);
var with_award = [];

function setDisabled(value, ins) {
  ins.forEach(x => {
    x.disabled = value;
    x.labels.forEach(l => {
      if (value) {
        l.classList.add("disabled");
      }
      else {
        l.classList.remove("disabled");
      }
    });
  });
}

function updateDisabled(value, others, group) {
  setDisabled(value, others);
  if (!value) {
    setDisabled(false, group);
  }
}

persona.addEventListener("input", function(event) {
  updateDisabled(persona.value, non_persona, with_persona);
}, false);

forename.addEventListener("input", function(event) {
  updateDisabled(forename.value || surname.value, non_forename, with_forename);
}, false);

surname.addEventListener("input", function(event) {
  updateDisabled(surname.value || forename.value, non_surname, with_surname);
}, false);

begin.addEventListener("input", function(event) {
  updateDisabled(begin.value || end.value, non_begin, with_begin);
}, false);

end.addEventListener("input", function(event) {
  updateDisabled(end.value || begin.value, non_end, with_end);
}, false);

crown.addEventListener("input", function(event) {
  updateDisabled(crown.value, non_crown, with_crown);
}, false);

award.addEventListener("input", function(event) {
  updateDisabled(award.value, non_award, with_award);
}, false);

form.addEventListener("reset", function(event) {
  updateDisabled(false, inputs, []);
}, false);
