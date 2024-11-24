const channels = document.getElementById("channels");

function addChannel(data) {
  console.log("Adding channel:", data);
  const channel = `
    <a id="${data.id}" class="w-full bg-gray-200 cursor-pointer px-4 py-2 hover:scale-[1.01] rounded" href="/tickets/${data.id}">
        ${data.topic}
    </a>
  `;
  channels.insertAdjacentHTML("beforeend", channel); // Use insertAdjacentHTML instead of appendChild
}

function removeTicket(id) {
  const ticket = document.getElementById(id);
  if (ticket) ticket.remove();
}

async function createTicket(event) {
  event.preventDefault(); // Prevent form from submitting the default way

  const form = event.target;
  const payload = {
    topic: form.topic.value,
    description: form.description.value,
  };

  console.log("Creating ticket with payload:", payload);
  if (!payload.topic || !payload.description) {
    showToast("Please fill in all fields", true);
    return;
  }

  console.log("Creating ticket with payload:", payload);

  try {
    const response = await fetch(`/api/v1/tickets`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: getToken(),
      },
      body: JSON.stringify(payload),
    });

    if (response.ok) {
      const data = await response.json();
      console.log("Ticket created successfully:", data);
      addChannel(data);
      showToast("Ticket created successfully!", false);
      window.location.href = `/tickets/${data.id}`;
    } else {
      const errorData = await response.json();
      showToast(
        `Error: ${
          errorData.message ||
          "Failed to create ticket :" + (await response.text())
        }`,
        true
      );
      console.log("Failed to create ticket:", errorData);
    }
  } catch (error) {
    showToast(`An unexpected error occurred: ${error.message}`, true);
    throw error;
  }
}

async function fetchChannels() {
  try {
    const response = await fetch(`/api/v1/tickets`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: getToken(),
        Accept: "application/json",
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error("Failed to fetch channels:", errorData);
      throw new Error(errorData.message);
    }

    const data = await response.json();
    const channels = document.getElementById("channels");
    channels.innerHTML = "";

    data.forEach((ticket) => addChannel(ticket));
  } catch (error) {
    showToast("Failed to fetch channels:", error);
    throw error;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  fetchChannels();

  const socket_url = "/";

  const socket = io(socket_url);
  socket.on("connect", () => {
    console.log("Connected to the server");
    socket.emit("authorize", { token: getToken() });
  });
  socket.on("disconnect", () => {
    console.log("Disconnected from the server");
  });

  socket.on("authorized", () => {
    console.log("Authorized successfully");
  });


  socket.on("ticket_closed", (data) => {
    console.log("Ticket Closed Removing:", data);
    removeTicket(data.id);

  });
  
});
