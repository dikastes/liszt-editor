const dmadOnDjangoSearchGnd = {
	init: config => {
		const input = document.querySelector(`#${config['input']}`);
		const type = config['entityType'];
		const gndTargetName = config['gnd-target'] ?? 'gnd_id';
		const designatorTargetName = config['designator-target'] ?? 'interim_designator';
		this.gndTarget = document.querySelector(`[name="${gndTargetName}"]`);
		this.designatorTarget = document.querySelector(`[name="${designatorTargetName}"]`);
		this.target = document.querySelector(`#${config['target']}`);
		const baseUrl = '/dmad/search-gnd/'

		input.addEventListener('input', _ => {
			const searchString = input.value;
			if (searchString.length < 3) {
				target.innerHTML = '<li><em> bitte Suchbegriff eingeben </em></li>';
			} else {
				fetch(`${baseUrl}${type}/${searchString}`)
					.then(response => { return response.json(); })
					.then(data => dmadOnDjangoSearchGnd.process(data));
			}
		})
	},

	process: data => {
		if (data.length > 0) {
			target.innerHTML = data.map(r => dmadOnDjangoSearchGnd.buildLink(r.id, r.label)).join('');
			document.querySelectorAll('.data-link').forEach(target => {
				target.addEventListener('click', e => {
					this.designatorTarget.value = e.target.dataset['label'];
					this.gndTarget.value = e.target.dataset['url'].replace('https://d-nb.info/gnd/', '');
				})
			})
		} else {
			target.innerHTML = '<li><em> keine Suchergebnisse </em></li>';
		}

	},

	buildLink : (url, label) => `<li>${label} <button href="#" class="data-link badge badge-primary" data-url="${url}" data-label="${label}">Daten übernehmen</button></li>`
}
