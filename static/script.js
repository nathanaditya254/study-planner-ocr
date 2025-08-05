const apiUrl = 'http://localhost:5000';

async function addTask() {
  const name = document.getElementById("task-name").value;
  const due_date = document.getElementById("task-due-date").value;
  const duration = document.getElementById("task-duration").value;
  const type = document.getElementById("task-type").value;

  const res = await fetch(`${apiUrl}/add-task`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, due_date, duration, type })
  });

  const data = await res.json();
  alert(data.message || "Task added");
}

async function startBreak() {
  const duration = document.getElementById("break-duration").value;

  const res = await fetch(`${apiUrl}/start-break`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ duration })
  });

  const data = await res.json();
  alert(`Break started. Ends at: ${new Date(data.end_time).toLocaleTimeString()}`);
}

async function fetchSchedule() {
  const res = await fetch(`${apiUrl}/schedule`);
  const data = await res.json();
  const list = document.getElementById("schedule-list");
  list.innerHTML = "";

  data.forEach(item => {
    const li = document.createElement("li");
    li.textContent = `${item.task} → ${item.start} to ${item.end}`;
    list.appendChild(li);
  });
}

async function fetchBreaks() {
  const res = await fetch(`${apiUrl}/breaks`);
  const data = await res.json();
  const list = document.getElementById("breaks-list");
  list.innerHTML = "";

  data.breaks.forEach(b => {
    const li = document.createElement("li");
    li.textContent = `Break: ${b.start_time} for ${b.duration} mins (End: ${b.end_time})`;
    list.appendChild(li);
  });
}
async function handleImageUpload(file) {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const uploadRes = await fetch(`${apiUrl}/upload`, {
      method: "POST",
      body: formData
    });

    const taskData = await uploadRes.json();
    if (taskData.error) {
      alert("OCR Error: " + taskData.error);
      return;
    }

    const addTaskRes = await fetch(`${apiUrl}/add-task`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(taskData)
    });

    const result = await addTaskRes.json();
    if (!result.error) {
      alert("Task added successfully!");
    } else {
      alert("Failed to add task: " + result.error);
    }
  } catch (err) {
    console.error("Image upload error:", err);
  }
}
async function uploadSelectedImage() {
  const file = document.getElementById("fileInput").files[0];
  if (!file) {
    alert("Please select an image first.");
    return;
  }

  await handleImageUpload(file);
  document.getElementById("fileInput").value = "";
}
