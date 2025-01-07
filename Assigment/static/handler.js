document.addEventListener("DOMContentLoaded", () => {
    const uploadForm = document.getElementById("uploadForm");
    const loaderContainer = document.getElementById("loaderContainer");

    function showLoader() {
        loaderContainer.style.display = "block";
    }

    function hideLoader() {
        loaderContainer.style.display = "none";
    }

    // Function to display custom popup
    function showPopup(message, isError = false) {
        const popup = document.createElement("div");
        popup.className = "popup";
        popup.style.position = "fixed";
        popup.style.top = "50%";
        popup.style.left = "50%";
        popup.style.transform = "translate(-50%, -50%)";
        popup.style.padding = "20px";
        popup.style.backgroundColor = isError ? "red" : "green";
        popup.style.color = "white";
        popup.style.borderRadius = "5px";
        popup.style.zIndex = "1000";
        popup.innerHTML = message;

        document.body.appendChild(popup);

        // Automatically close the popup after 5 seconds
        setTimeout(() => {
            document.body.removeChild(popup);
        }, 5000);
    }

    async function uploadFile(event) {
        event.preventDefault();

        const formData = new FormData();
        const usersFile = document.querySelector("input[name='usersfile']").files[0];
        const ordersFile = document.querySelector("input[name='orderfile']").files[0];
        const productsFile = document.querySelector("input[name='productfile']").files[0];

        if (!usersFile || !ordersFile || !productsFile) {
            alert("Please upload all the required files.");
            return;
        }

        formData.append("users", usersFile);
        formData.append("orders", ordersFile);
        formData.append("products", productsFile);

        try {
            showLoader();

            const response = await fetch("/upload/upload-csv/", {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": document.querySelector("input[name='csrfmiddlewaretoken']").value
                }
            });

            const result = await response.json();

            hideLoader();

            if (response.ok) {
                // Check for transaction failure
                if (result.error && result.error.includes("Transaction failed")) {
                    showPopup("Transaction Failed: " + result.error, true);  // Display the error popup
                } else {
                    showPopup("Success: " + result.message);  // Display success popup
                }
            } else {
                showPopup("Error: " + (result.error || "An unknown error occurred."), true);  // Display error popup
            }
        } catch (error) {
            hideLoader();
            showPopup("An error occurred: " + error.message, true);  // Display error popup
        }
    }

    uploadForm.addEventListener("submit", uploadFile);
});
