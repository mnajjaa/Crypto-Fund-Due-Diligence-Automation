console.log("🚀 Sanctions script loaded!");

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("sanctions-form");
    const walletInput = document.getElementById("wallet-address");
    const chainSelect = document.getElementById("chain-select");
    const submitButton = document.getElementById("submit-button");
    const resultDiv = document.getElementById("result");
    const sanctionStatus = document.getElementById("sanction-status");
    const sanctionDetails = document.getElementById("sanction-details");
    const walletNetworthDiv = document.getElementById("wallet-networth");
    const walletTokensDiv = document.getElementById("wallet-tokens");

    // Enable / disable the submit button
    walletInput.addEventListener("input", function () {
        submitButton.disabled = walletInput.value.trim() === "";
    });

    form.addEventListener("submit", async function (e) {
        e.preventDefault();
        const walletAddress = walletInput.value.trim();
        const chain = chainSelect.value; // 🆕 get user-selected chain

        if (!walletAddress) {
            resultDiv.innerHTML = "<p class='text-danger'>Please enter a wallet address.</p>";
            return;
        }

        try {
            // Reset previous results
            resultDiv.innerHTML = "";
            walletNetworthDiv.innerHTML = "";
            walletTokensDiv.innerHTML = "";
            sanctionDetails.innerHTML = "";

            const response = await fetch("/sanctions/check/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": getCSRFToken()
                },
                body: `wallet_address=${encodeURIComponent(walletAddress)}&chain=${encodeURIComponent(chain)}`
            });

            const data = await response.json();

            // 🔴 If there's an error from server
            if (data.error) {
                resultDiv.innerHTML = `<p class='text-danger'>Error: ${data.error}</p>`;
                sanctionStatus.classList.remove("badge-success", "badge-danger");
                sanctionStatus.classList.add("badge-warning");
                sanctionStatus.innerText = "Error Checking";
                return;
            }

            // ========================
            // 1) SANCTIONS LOGIC
            // ========================
            if (data.identifications && data.identifications.length > 0) {
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

            // ========================
            // 2) MORALIS TOKEN BALANCES
            // ========================
            if (Array.isArray(data.moralis_tokens)) {
                if (data.moralis_tokens.length > 0) {
                    const tokenList = data.moralis_tokens.map(token => {
                        const tokenName = token.symbol || token.name || "Unknown";
                        const decimals = token.decimals ? parseInt(token.decimals) : 18;
                        // fallback if decimals is missing
                        const balanceNum = parseFloat(token.balance_formatted) ||
                            parseFloat(token.balance) / (10 ** decimals) ||
                            0;

                        return `
                            <li class="list-group-item">
                                <img src="${token.logo || '#'}" alt="logo" style="width:16px;height:16px;margin-right:4px;">
                                <strong>${tokenName}</strong>:
                                ${balanceNum.toFixed(4)} 
                                ${token.usd_price ? `(~$${(balanceNum * token.usd_price).toFixed(2)})` : ''}
                                ${token.possible_spam ? `<span class="badge bg-warning text-dark ms-2">Spam?</span>` : ''}
                            </li>`;
                    }).join("");

                    walletTokensDiv.innerHTML = `
                        <h6>Token Balances on ${chain.toUpperCase()}</h6>
                        <ul class="list-group list-group-flush">${tokenList}</ul>
                    `;
                } else {
                    walletTokensDiv.innerHTML = `<p class='text-muted'>No tokens found on ${chain.toUpperCase()}.</p>`;
                }
            }

            // ========================
            // 3) MORALIS NET WORTH
            // ========================
            if (data.moralis_networth && data.moralis_networth.total_networth_usd) {
                const usdValue = parseFloat(data.moralis_networth.total_networth_usd).toFixed(2);
                walletNetworthDiv.innerHTML = `<p><strong>💰 Net Worth:</strong> $${usdValue}</p>`;
            } else {
                walletNetworthDiv.innerHTML = `<p class='text-muted'>Net worth data not available.</p>`;
            }
            

        } catch (error) {
            console.error(error);
            resultDiv.innerHTML = `<p class='text-danger'>Failed to check sanctions.</p>`;
            sanctionStatus.classList.add("badge-warning");
            sanctionStatus.innerText = "Error Checking";
        }
    });

    function getCSRFToken() {
        return document.cookie.split("; ").find(row => row.startsWith("csrftoken"))?.split("=")[1];
    }
});
