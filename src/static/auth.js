async function signUp(event) {
  console.log("signUp");
  event.preventDefault();

  const form = event.target;
  const payload = {
    email: form.email.value,
    username: form.username.value,
    id: form.user_id.value,
  };

  const response = await fetch("/api/v1/auth/signup", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (response.ok) {
    const { token } = await response.json();
    localStorage.setItem("token", token);
    window.location.href = "/support";
  } else {
    try {
      const { message } = await response.json().message;
      showToast(message, true);
    } catch (error) {
        showToast("Something went wrong" + error, true);
    }
  }
}


