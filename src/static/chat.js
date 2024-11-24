const messages = document.getElementById("messages");
const messageSection = document.getElementById("message-section");
var user_id = null;

function getChannelID() {
  const pathSegments = window.location.pathname.split("/");
  return pathSegments[pathSegments.length - 1];
}

function addMessage(data) {
  if (data.author_id == user_id) {
    const message = `
        <div id=${data.id} class="self-end bg-blue-500 text-white max-s-xs rounded-lg px-3 py-1.5 text-sm">
            ${data.content}
        </div>
        `;
    messageSection.insertAdjacentHTML("beforeend", message);
  } else {
    const message = `
        <div id=${data.id} class="self-start bg-gray-200 text-gray-800 max-w-xs rounded-lg px-3 py-1.5 text-sm">
            ${data.content}
        </div>
        `;
    messageSection.insertAdjacentHTML("beforeend", message);
  }
}

async function sendMessage(event) {
  event.preventDefault();

  const payload = {
    content: event.target.message.value,
  };

  if (!payload.content) {
    showToast("Please enter a message", true);
    return;
  }
  
  event.target.message.value = "";

  try {
    const response = await fetch(`/api/v1/tickets/${getChannelID()}/messages`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: getToken(),
      },
      body: JSON.stringify(payload),
    });

    if (response.ok) {
      const data = await response.json();
      console.log("Message sent successfully:", data);
      addMessage(data);
    } else {
      const errorData = await response.json();
      showToast(
        `Error: ${errorData.message || "Failed to send message"}`,
        true
      );
      console.error("Failed to send message:", errorData);
    }
  } catch (error) {
    showToast(`An unexpected error occurred: ${error.message}`, true);
    throw new Error(error);
  }
}

async function fetchTicket() {
  const channel_id = getChannelID();
  try {
    const response = await fetch(`/api/v1/tickets/${channel_id}`, {
      headers: {
        Authorization: getToken(),
      },
    });

    if (response.ok) {
      const data = await response.json();
      console.log("Ticket data:", data);
      user_id = data.user_id;
    } else {
      const errorData = await response.json();
      showToast(
        `Error: ${errorData.message || "Failed to fetch ticket"}`,
        true
      );
      console.error("Failed to fetch ticket:", errorData);
    }
  } catch (error) {
    showToast(`An unexpected error occurred: ${error.message}`, true);
    throw new Error(error);
  }
}

async function fetchMessages() {
  const channel_id = getChannelID();
  try {
    const response = await fetch(`/api/v1/tickets/${channel_id}/messages`, {
      headers: {
        Authorization: getToken(),
      },
    });

    if (response.ok) {
      const data = await response.json();
      console.log("Messages data:", data);
      data.forEach(addMessage);
    } else {
      const errorData = await response.json();
      showToast(
        `Error: ${errorData.message || "Failed to fetch messages"}`,
        true
      );
      console.error("Failed to fetch messages:", errorData);
    }
  } catch (error) {
    showToast(`An unexpected error occurred: ${error.message}`, true);
    throw new Error(error);
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  await fetchTicket();
  await fetchMessages();

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
    console.log("Ticket closed:", data);
    showToast("Ticket closed by the support agent");
    window.location.href = "/support";
  });

  socket.on("message", (data) => {
    console.log("Received message:", data);
    addMessage(data);
  });

  socket.on("edit_message", (data) => {
    console.log("Message Edited:", data);
    const messageElement = document.getElementById(data.id);
    messageElement.innerText = `${data.content}`;
  });

  socket.on("delete_message", (data) => {
    console.log("Message Deleted:", data);
    const messageElement = document.getElementById(data.id);
    messageElement.remove();
  });


});
