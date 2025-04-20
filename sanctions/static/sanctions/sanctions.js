console.log("🚀 Sanctions script loaded!");

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("sanctions-form");
    const walletInput = document.getElementById("wallet-address");
    const chainSelect = document.getElementById("chain-select");
    const submitButton = document.getElementById("submit-button");
    const resultDiv = document.getElementById("result");
    const sanctionStatus = document.getElementById("sanction-status");
    const sanctionCards = document.getElementById("sanction-inner-cards");
    const altWalletsBlock = document.getElementById("alt-wallets-block");
    const descriptionBlock = document.getElementById("description-block");

    walletInput.addEventListener("input", function () {
        submitButton.disabled = walletInput.value.trim() === "";
    });

    form.addEventListener("submit", async function (e) {
        e.preventDefault();
        const walletAddress = walletInput.value.trim();
        const chain = chainSelect.value;

        if (!walletAddress) {
            resultDiv.innerHTML = "<p class='text-danger'>Please enter a wallet address.</p>";
            return;
        }

        try {
            resultDiv.innerHTML = "";
            sanctionCards.innerHTML = "";
            altWalletsBlock.innerHTML = "";
            descriptionBlock.innerHTML = "";

            const response = await fetch("/sanctions/check/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": getCSRFToken()
                },
                body: `wallet_address=${encodeURIComponent(walletAddress)}&chain=${encodeURIComponent(chain)}`
            });

            const data = await response.json();

            if (data.error) {
                resultDiv.innerHTML = `<p class='text-danger'>Error: ${data.error}</p>`;
                sanctionStatus.classList.remove("badge-success", "badge-danger");
                sanctionStatus.classList.add("badge-warning");
                sanctionStatus.innerText = "Error Checking";
                return;
            }

            if (data.identifications && data.identifications.length > 0) {
                const ident = data.identifications[0];
                const name = ident.name || "N/A";
                const description = ident.description || "No description available.";

                const urlMatch = description.match(/https?:\/\/\S+/g);
                const referenceURL = urlMatch ? urlMatch[urlMatch.length - 1] : null;
                const emailMatches = description.match(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z]{2,}\b/gi);
                const dobMatch = description.match(/DOB\s+(\d{2}\s\w+\s\d{4})/i);
                const passportMatch = description.match(/Passport\s+([\w\d]+)/i);
                const nationalityMatch = description.match(/nationality\s+([A-Za-z]+)/i);
                const altWallets = description.match(/0x[a-fA-F0-9]{40}/g)?.slice(1);

                sanctionStatus.classList.remove("badge-success");
                sanctionStatus.classList.add("badge-danger");
                sanctionStatus.innerText = "Sanctioned";

                const leftCard = `
                    <div class="card p-3 shadow-sm h-100">
                        <p><strong>Name:</strong> ${name}</p>
                        <p><strong>Date of Birth:</strong> ${dobMatch ? dobMatch[1] : 'N/A'}</p>
                        <p><strong>Nationality:</strong> ${nationalityMatch ? nationalityMatch[1] : 'N/A'}</p>
                        <p><strong>Passport No.:</strong> ${passportMatch ? passportMatch[1] : 'N/A'}</p>
                        ${emailMatches ? `<p><strong>Emails:</strong><br>${emailMatches.join('<br>')}</p>` : ''}
                        ${referenceURL ? `<p><strong>Source:</strong> <a href="${referenceURL}" target="_blank">${referenceURL}</a></p>` : ''}
                    </div>`;

                const rightCard = `
                    <div class="card p-3 shadow-sm h-100 d-flex flex-column justify-content-between">
                        <div>
                          <h6>Wallet Profile (via Moralis)</h6>
                          <div id="moralis-networth"></div>
                          <div id="moralis-tokens"></div>
                        </div>
                        <div class="text-center mt-3">
                          <a href="#" class="text-primary small">Show more ▼</a>
                        </div>
                    </div>`;

                sanctionCards.innerHTML = `
                    <div class="col-md-6 d-flex">${leftCard}</div>
                    <div class="col-md-6 d-flex">${rightCard}</div>`;

                const networthDiv = document.getElementById("moralis-networth");
                const tokensDiv = document.getElementById("moralis-tokens");

                if (data.moralis_networth && data.moralis_networth.total_networth_usd) {
                    const usdValue = parseFloat(data.moralis_networth.total_networth_usd).toFixed(2);
                    networthDiv.innerHTML = `<p><strong>💰 Net Worth:</strong> $${usdValue}</p>`;
                } else {
                    networthDiv.innerHTML = `<p class='text-muted'>Net worth data not available.</p>`;
                }

                if (Array.isArray(data.moralis_tokens)) {
                    if (data.moralis_tokens.length > 0) {
                        const tokenList = data.moralis_tokens.map(token => {
                            const tokenName = token.symbol || token.name || "Unknown";
                            const decimals = token.decimals ? parseInt(token.decimals) : 18;
                            const balanceNum = parseFloat(token.balance_formatted) ||
                                parseFloat(token.balance) / (10 ** decimals) ||
                                0;

                            return `<li class="list-group-item">
                                <img src="${token.logo || '#'}" alt="logo" style="width:16px;height:16px;margin-right:4px;">
                                <strong>${tokenName}</strong>: ${balanceNum.toFixed(4)}
                                ${token.usd_price ? `(~$${(balanceNum * token.usd_price).toFixed(2)})` : ''}
                                ${token.possible_spam ? `<span class="badge bg-warning text-dark ms-2">Spam?</span>` : ''}
                            </li>`;
                        }).join("");

                        tokensDiv.innerHTML = `
                            <ul class="list-group list-group-flush">${tokenList}</ul>`;
                    } else {
                        tokensDiv.innerHTML = `<p class='text-muted'>No tokens found on ${chain.toUpperCase()}.</p>`;
                    }
                }
            } else {
                sanctionStatus.classList.remove("badge-danger");
                sanctionStatus.classList.add("badge-success");
                sanctionStatus.innerText = "Not Sanctioned";
                sanctionCards.innerHTML = "<p class='text-success'>This address is not sanctioned.</p>";
            }

            if (data.identifications && data.identifications.length > 0) {
                const ident = data.identifications[0];
                const description = ident.description || "";
                const altWallets = description.match(/0x[a-fA-F0-9]{40}/g)?.slice(1);

                if (altWallets && altWallets.length) {
                    const maxToShow = 3;
                    const shown = altWallets.slice(0, maxToShow).join('<br>');
                    const hidden = altWallets.slice(maxToShow).join('<br>');
                    const hasHidden = altWallets.length > maxToShow;
                    altWalletsBlock.innerHTML = `
                        <strong>Alt Wallets:</strong><br>
                        ${shown}
                        ${hasHidden ? `<span id="alt-wallets-toggle" class="collapse">${hidden}</span>
                        <a href="#" data-bs-toggle="collapse" data-bs-target="#alt-wallets-toggle" class="ms-1 small text-primary">Read more</a>` : ''}`;
                }

                if (description.length > 250) {
                    const shortDesc = description.slice(0, 250);
                    descriptionBlock.innerHTML = `
                        <strong>Description:</strong><br>
                        <span id="desc-short">${shortDesc}...</span>
                        <span id="desc-full" class="collapse">${description}</span>
                        <a href="#" data-bs-toggle="collapse" data-bs-target="#desc-full" class="ms-1 small text-primary">Read more</a>`;
                } else {
                    descriptionBlock.innerHTML = `<strong>Description:</strong><br><p>${description}</p>`;
                }
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
