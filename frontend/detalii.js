const API_BASE_URL = window.API_BASE_URL || 'http://127.0.0.1:8000/api';
const containerDetalii = document.querySelector('#detaliiRestaurant');
const parametriUrl = new URLSearchParams(window.location.search);
const idDinUrl = parametriUrl.get('id');

function genereazaSlug(numeRestaurant) {
    return numeRestaurant
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, '')
        .trim()
        .replace(/\s+/g, '-');
}

function construiesteLinkMaps(numeRestaurant, locatieRestaurant) {
    const interogareMaps = encodeURIComponent(`${numeRestaurant} ${locatieRestaurant}`);
    return `https://www.google.com/maps/search/?api=1&query=${interogareMaps}`;
}

function afiseazaEroare(textEroare) {
    containerDetalii.innerHTML = `<p class="mesaj-eroare">${textEroare}</p><a class="btn site-btn detalii-btn" href="index.html#menu">Inapoi la cautare</a>`;
}

function afiseazaDetaliiRestaurant(restaurantGasit) {
    const listaMeniuHtml = (restaurantGasit.meniu || [])
        .map((produs) => `<li><span>${produs.numeProdus}</span><strong>${produs.pret} RON</strong></li>`)
        .join('');

    const linkOficial = restaurantGasit.linkOficial || construiesteLinkMaps(restaurantGasit.nume, restaurantGasit.locatie);

    containerDetalii.innerHTML = `
        <a class="btn site-btn detalii-btn" href="index.html#menu">Inapoi la cautare</a>
        <h1>${restaurantGasit.nume}</h1>
        <img class="detalii-imagine" src="${restaurantGasit.imagine}" alt="${restaurantGasit.nume}">
        <p><strong>Specific:</strong> ${restaurantGasit.specific}</p>
        <p><strong>Locatie:</strong> ${restaurantGasit.locatie}</p>
        <a class="btn detalii-btn site-btn" href="${linkOficial}" target="_blank" rel="noopener noreferrer">Pagina oficiala</a>
        <h2>Meniu</h2>
        <ul class="lista-meniu">
            ${listaMeniuHtml}
        </ul>
    `;
}

function cautaRestaurantLocalDupaSlug(slug) {
    if (!Array.isArray(window.restauranteBaiaMare)) {
        return null;
    }

    return window.restauranteBaiaMare.find((restaurant) => genereazaSlug(restaurant.nume) === slug) || null;
}

async function incarcaDetaliiRestaurant() {
    if (!idDinUrl) {
        afiseazaEroare('Lipseste id-ul restaurantului din URL.');
        return;
    }

    try {
        const raspuns = await fetch(`${API_BASE_URL}/restaurants/${encodeURIComponent(idDinUrl)}`);

        if (raspuns.status === 404) {
            const restaurantLocal = cautaRestaurantLocalDupaSlug(idDinUrl);
            if (restaurantLocal) {
                afiseazaDetaliiRestaurant(restaurantLocal);
                return;
            }

            afiseazaEroare('Restaurantul cautat nu a fost gasit.');
            return;
        }

        if (!raspuns.ok) {
            throw new Error(`Eroare API: ${raspuns.status}`);
        }

        const restaurantGasit = await raspuns.json();
        afiseazaDetaliiRestaurant(restaurantGasit);
    } catch (eroare) {
        const restaurantLocal = cautaRestaurantLocalDupaSlug(idDinUrl);
        if (restaurantLocal) {
            afiseazaDetaliiRestaurant(restaurantLocal);
            return;
        }

        afiseazaEroare('Nu am putut incarca datele din backend sau din fisierul local.');
    }
}

incarcaDetaliiRestaurant();
