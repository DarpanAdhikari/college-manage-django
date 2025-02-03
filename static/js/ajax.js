$(document).ready(function () {
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  const csrftoken = getCookie("csrftoken");
  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      if (
        !/^GET|HEAD|OPTIONS|TRACE$/.test(settings.type) &&
        !this.crossDomain
      ) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    },
  });
  if (
    $("#course_code".length || $("#id_course").length) &&
    $("#semester").length
  ) {
    var courseCode = $("#course_code").length
      ? $("#course_code")
      : $("#id_course");
    if (courseCode.val()) {
      getSemester(courseCode.val());
    }

    courseCode.change(function () {
      var courseId = $(this).val();
      getSemester(courseId);
    });

    function getSemester(val) {
      if (val !== "") {
        $.ajax({
          url: "/semester-request/",
          type: "POST",
          data: { course_id: val },
          dataType: "json",
          success: function (data) {
            $("#semester").empty();
            let sem = courseCode.attr("data-sem");
            if (data.semesters.length > 0) {
              var select = $("#semester");
              select.append($("<option></option>").attr("value", "").text("Select semester"));
              $.each(data.semesters, function (index, semester) {
                var option = $("<option></option>")
                  .attr("value", semester.sem_id)
                  .text(semester.semester);
                if (sem == semester.sem_id) {
                  option.prop("selected", true);
                }
                select.append(option);
              });
            } else {
              $("#semester").html(
                '<option value="">No semester available</option>'
              );
            }
          },
          error: function (xhr, status, error) {
            console.error("AJAX Error: " + status + " " + error);
          },
        });
      } else {
        $("#semester").html('<option value="">No semester</option>');
      }
    }
  }

  let popupWindow = null;
  const $actionBtn = $("#attendance-action");
  const $semester = $("#semester");

  // Function to open or focus on the popup window
  const openPopup = (title, identifier) => {
    if (!popupWindow || popupWindow.closed) {
      const url = `/scanner/?id=${identifier}`;
      popupWindow = window.open(url, "qr-scanner", "width=600,height=400");
      $(popupWindow).on("load", () => {
        popupWindow.document.title = title;
      });
      const checkPopupClosed = setInterval(() => {
        if (popupWindow.closed) {
          clearInterval(checkPopupClosed);
          $actionBtn.text("Start Attendance");
          $semester.val("");
        }
      }, 1000);
    } else {
      popupWindow.focus();
    }
  };

  $actionBtn.on("click", function () {
    if ($actionBtn.text() === "Start Attendance") {
      $actionBtn.text("Stop Attendance");
      openPopup(document.title, "teacher");
    } else {
      if (popupWindow && !popupWindow.closed) {
        popupWindow.close();
        $actionBtn.text("Start Attendance");
      }
    }
  });

  $semester.on("change", function () {
    if ($(this).val().trim() !== "") {
      let link = window.location.href;
      if (
        $("#course_code").attr("data-url") &&
        link.includes($("#course_code").attr("data-url"))
      ) {
        let cam = $("#course_code").attr("data-cam") === "True";
        let value = "";
        if (cam) {
          value = "&popup=true";
        }
        window.location.href =
          $("#course_code").attr("data-url") +
          "?sem=" +
          $(this).val().trim() +
          value;
      }
    } else {
      if (popupWindow && !popupWindow.closed) {
        popupWindow.close();
      }
    }
  });
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('popup') === 'true') {
      openPopup(document.title, "student");
  }
  $(window).on("beforeunload", function (e) {
    if (popupWindow && !popupWindow.closed) {
      popupWindow.close();
      e.preventDefault();
      e.returnValue = "";
    }
  });
  $(window).on("message", function (event) {
    if (event.originalEvent.origin === window.location.origin) {
      if (event.originalEvent.data.type === "popupMessage") {
        const messageData = event.originalEvent.data.data;
        const identifier = event.originalEvent.data.id;
        if (identifier == "teacher") {
          takeTeacherAttendance(messageData);
        } else if (identifier == "student") {
          takeStudentAttendance(messageData,$('#course_code').val(),$('#semester').val());
        }
      }
    }
  });

  async function takeTeacherAttendance(data) {
    try {
      const teacherData = JSON.parse(data);
      const response = await $.ajax({
        url: "/take-teacher-attendance/",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({ teacher: teacherData }),
        dataType: "json",
      });
      if (response) {
        if ($("#attendance-table").parent().is(":hidden")) {
          $("#attendance-table").parent().show();
        }
        $("#attendance-table").append(`<tr>
        <th scope="row">${$("#attendance-table tr").length + 1}</th>
        <td scope="row">${response.name}</td>
        <td scope="row">${response.username}</td>
        <td scope="row"><span class="badge bg-success">${
          response.date
        }</span></td>
      </tr>`);
      queueUtterance('welcome,'+response.name)
      }
    } catch (error) {
      // console.error("AJAX Error:", error);
    }
  }
  async function takeStudentAttendance(data, course, sem) {
    if (!data || !course || !sem) {
        alert('Invalid request method');
        return;
    }

    try {
        const studentData = typeof data === 'string' ? JSON.parse(data) : data;
        const response = await $.ajax({
            url: "/take-student-attendance/",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ student: studentData, course: course, sem: sem }),
            dataType: "json",
        });
        if (response) {
          if ($("#attendance-table").parent().is(":hidden")) {
            $("#attendance-table").parent().show();
          }
          $("#attendance-table").append(`<tr>
          <th scope="row">${$("#attendance-table tr").length + 1}</th>
          <td scope="row">${response.name}</td>
          <td scope="row">${response.username}</td>
          <td scope="row"><span class="badge bg-success">${
            response.date
          }</span></td>
        </tr>`);
        queueUtterance('welcome,'+response.name)
        }
    } catch (error) {
        console.error("AJAX Error:", error);
    }
}

});
if ($("#attendance-table tbody tr").length < 1) {
  $("#attendance-table").parent().hide();
}
// speaking---------------------------------
let queue = [];
let speaking = false;

function speakNext() {
  if (queue.length > 0 && !speaking) {
    speaking = true;
    const utterance = queue.shift();
    utterance.onend = () => {
      speaking = false;
      speakNext();
    };
    speechSynthesis.speak(utterance);
  }
}
function queueUtterance(text) {
  const utterance = new SpeechSynthesisUtterance(text);
  queue.push(utterance);
  speakNext();
}