document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("sanctions-form");
    const walletInput = document.getElementById("wallet-address");
    const submitButton = document.getElementById("submit-button");
    const resultDiv = document.getElementById("result");
    const sanctionStatus = document.getElementById("sanction-status");
    const sanctionDetails = document.getElementById("sanction-details");

    // Enable button only when input is not empty
    walletInput.addEventListener("input", function () {
        submitButton.disabled = walletInput.value.trim() === "";
    });

    form.addEventListener("submit", async function (e) {
        e.preventDefault();
        const walletAddress = walletInput.value.trim();

        if (!walletAddress) {
            resultDiv.innerHTML = "<p class='text-danger'>Please enter a wallet address.</p>";
            return;
        }

        try {
            const response = await fetch("/sanctions/check/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": getCSRFToken()
                },
                body: `wallet_address=${walletAddress}`
            });

            const data = await response.json();

            if (data.error) {
                resultDiv.innerHTML = `<p class='text-danger'>Error: ${data.error}</p>`;
                sanctionStatus.classList.remove("badge-success", "badge-danger");
                sanctionStatus.classList.add("badge-warning");
                sanctionStatus.innerText = "Error Checking";
            } else if (data.identifications && data.identifications.length > 0) {
                sanctionStatus.classList.remove("badge-success");
                sanctionStatus.classList.add("badge-danger");
                sanctionStatus.innerText = "Sanctioned";

                sanctionDetails.innerHTML = `
                    <p><strong>Name:</strong> ${data.identifications[0]?.name || "N/A"}</p>
                    <p><strong>Description:</strong> ${data.identifications[0]?.description || "N/A"}</p>
                `;
            } else {
                sanctionStatus.classList.remove("badge-danger");
                sanctionStatus.classList.add("badge-success");
                sanctionStatus.innerText = "Not Sanctioned";
                sanctionDetails.innerHTML = "<p class='text-success'>This address is not sanctioned.</p>";
            }

        } catch (error) {
            resultDiv.innerHTML = `<p class='text-danger'>Failed to check sanctions.</p>`;
            sanctionStatus.classList.add("badge-warning");
            sanctionStatus.innerText = "Error Checking";
        }
    });

    function getCSRFToken() {
        return document.cookie.split("; ").find(row => row.startsWith("csrftoken"))?.split("=")[1];
    }
});
