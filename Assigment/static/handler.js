document.addEventListener("DOMContentLoaded", () => {
    const uploadForm = document.getElementById("uploadForm");
    const loaderContainer = document.getElementById("loaderContainer");

    function showLoader() {
        loaderContainer.style.display = "block";
    }

    function hideLoader() {
        loaderContainer.style.display = "none";
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
                alert("Success: " + result.message);
            } else {
                alert("Error: " + (result.error || "An unknown error occurred."));
            }
        } catch (error) {
            hideLoader();
            alert("An error occurred: " + error.message);
        }
    }

    uploadForm.addEventListener("submit", uploadFile);
});
