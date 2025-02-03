const hamBurger = document.querySelector(".toggle-btn");
hamBurger.addEventListener("click", function () {
  document.querySelector("#sidebar").classList.toggle("expand");
});
const pastDatePick = document.querySelectorAll(".pastDate");
pastDatePick.forEach((pick) => {
  pick.max = new Date().toISOString().split("T")[0];
});

document.addEventListener('DOMContentLoaded', function() {
  const subjectFieldsContainer = document.getElementById('subject_fields');
  const addFieldButton = document.getElementById('addFieldButton');
  let fieldCount = 0;
  if(addFieldButton && subjectFieldsContainer){
  addFieldButton.addEventListener('click', function(e) {
    e.preventDefault();
    const fieldSet = document.createElement('div');
    fieldSet.className = 'row mt-3';
    fieldSet.id = `fieldSet_${fieldCount}`;

    fieldSet.innerHTML = `
    <div class="col-md-2">
        <div class="form-group">
            <label for="subject_code">Subject Code:</label>
            <input type="text" name="subject_code[]" class="form-control" placeholder="Enter Subject Code" required>
        </div>
    </div>
    <div class="col-md-3">
        <div class="form-group">
            <label for="subject_name">Subject Name:</label>
            <input type="text" name="subject_name[]" class="form-control" placeholder="Enter Subject Name" required>
        </div>
    </div>
    <div class="col-md-2">
        <div class="form-group">
            <label for="full_marks">Full Marks:</label>
            <input type="number" name="full_marks[]" class="form-control" placeholder="60" required>
        </div>
    </div>
    <div class="col-md-2">
        <div class="form-group">
            <label for="pass_marks">Pass Marks:</label>
            <input type="number" name="pass_marks[]" class="form-control" placeholder="24" required>
        </div>
    </div>
    <div class="col-md-2">
        <div class="form-group">
            <label for="credit_hours">Credit Hours:</label>
            <input type="number" name="credit_hours[]" class="form-control" placeholder="3" required>
        </div>
    </div>
    <div class="col-md-1">
        <button type="button" class="btn btn-danger btn-sm" onclick="removeField('${fieldCount}')">
            -
        </button>
    </div>
`;

    subjectFieldsContainer.appendChild(fieldSet);
    fieldCount++;
  });
}
});

function removeField(id) {
  const fieldSet = document.getElementById(`fieldSet_${id}`);
  if (fieldSet) {
    fieldSet.remove();
  }
}

// auto click and critical even for form
document.querySelectorAll('.autoClick').forEach(btn => {
  btn.click();
});
document.querySelectorAll('.criticalInput').forEach(input => {
  let previousValue = input.value;
  input.addEventListener('change', (e) => {
     if((previousValue.trim()) !=='' && (previousValue.trim() > e.target.value)){
      if (!confirm(`If you are reducing ${input.getAttribute("name")} value. It could delete related Data to those ${input.getAttribute("name")}`)) {
          input.value = previousValue;
      } else {
          previousValue = e.target.value;
      }
     }
  });
});

const amountField = document.querySelectorAll('.number');
amountField.forEach(num=>{
  num.addEventListener('input',(e)=>{
    const value = e.target.value;
    if (/[^0-9]/.test(value)) {
      e.target.value = value.replace(/[^0-9]/g, '');
    }
  })
})