async function fetchPersonData () {
    try {
        const url = `${location.origin}/edwoca/persons`;
        const response = await fetch(url);
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new Error('no JSON in the response');
        }
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();

        $('textarea').atwho({ at: '@', data: data });

    } catch (error) {
        console.error('There has been a problem with your fetch operation:', error);
    }
}

fetchPersonData();
$(document).ready(_ => {
    $('select.autocomplete-select').SumoSelect({search: true});
})
