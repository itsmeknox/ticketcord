const toast = document.getElementById("toast");
const toastMessage = document.getElementById("toast-message");



function showToast(message, error=false) {
    if (error == true) {
        toast.classList.add("bg-red-500");
    } else {
        toast.classList.remove("bg-green-500");
    }
    toastMessage.textContent = message;
    toast.classList.remove("hidden");

    setTimeout(() => {
        toast.classList.add("hidden");
    }, 3000); 
}

function getToken() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/auth';
    }

    return token;
}