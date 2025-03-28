console.log("🚀 Sanctions script loaded!");

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("sanctions-form");
    const walletInput = document.getElementById("wallet-address");
    const submitButton = document.getElementById("submit-button");
    const resultDiv = document.getElementById("result");
    const sanctionStatus = document.getElementById("sanction-status");
    const sanctionDetails = document.getElementById("sanction-details");

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
                const ident = data.identifications[0];
                const name = ident.name || "N/A";
                const description = ident.description || "No description available.";

                console.log("Parsing sanctioned result:", description);

                // Parse extras
                const urlMatch = description.match(/https?:\/\/\S+/g);
                const referenceURL = urlMatch ? urlMatch[urlMatch.length - 1] : null;

                const emailMatches = description.match(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z]{2,}\b/gi);
                const dobMatch = description.match(/DOB\s+(\d{2}\s\w+\s\d{4})/i);
                const passportMatch = description.match(/Passport\s+([\w\d]+)/i);
                const nationalityMatch = description.match(/nationality\s+([A-Za-z]+)/i);
                const altWallets = description.match(/0x[a-fA-F0-9]{40}/g)?.slice(1); // skip primary

                sanctionStatus.classList.remove("badge-success");
                sanctionStatus.classList.add("badge-danger");
                sanctionStatus.innerText = "Sanctioned";

                sanctionDetails.innerHTML = `
                <div class="mt-3">
                    <ul class="list-group list-group-flush">
                    <li class="list-group-item"><strong>Name:</strong> ${name}</li>
                    <li class="list-group-item"><strong>Date of Birth:</strong> ${dobMatch ? dobMatch[1] : 'N/A'}</li>
                    <li class="list-group-item"><strong>Nationality:</strong> ${nationalityMatch ? nationalityMatch[1] : 'N/A'}</li>
                    <li class="list-group-item"><strong>Passport No.:</strong> ${passportMatch ? passportMatch[1] : 'N/A'}</li>
                    ${emailMatches ? `<li class="list-group-item"><strong>Emails:</strong> ${emailMatches.join(', ')}</li>` : ''}
                    ${altWallets && altWallets.length ? `<li class="list-group-item"><strong>Alt Wallets:</strong><br>${altWallets.join('<br>')}</li>` : ''}
                    ${referenceURL ? `<li class="list-group-item"><strong>Source:</strong> <a href="${referenceURL}" target="_blank">${referenceURL}</a></li>` : ''}
                    </ul>
                    <div class="mt-3"><strong>Description:</strong><br>${description}</div>
                </div>
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


