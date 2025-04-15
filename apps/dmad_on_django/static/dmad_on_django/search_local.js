const dmadOnDjangoSearchLocal = {
	init: config => {
		const target = document.querySelector(`#${config['target']}`);
		const input = document.querySelector(`#${config['input']}`);
		const stubToggle = document.querySelector(`#${config['stubToggle']}`)
		const reworkToggle = document.querySelector(`#${config['reworkToggle']}`)
		const data = config['data'];
		const options = {
			keys: ['designator']
		}
		const fuse = new Fuse(data, options);

		const stubs = data.filter(e => e.gnd_id == null);
		const reworks = data.filter(e => e.rework_in_gnd);

		stubToggle.innerHTML += `<span class="badge">${stubs.length}</span>`;
		reworkToggle.innerHTML += `<span class="badge">${reworks.length}</span>`;

		input.addEventListener('input', _ => {
			const searchString = input.value;
			if (searchString == '') {
				target.innerHTML = '<li><em> bitte Suchbegriff eingeben </em></li>';
			} else {
				const results = fuse.search(searchString, {limit: 5});
				if (results.length > 0) {
					target.innerHTML = results.map(r => r.item.rendered_link).join('');
				} else {
					target.innerHTML = '<li><em> keine Suchergebnisse </em></li>';
				}
			}
		})

		stubToggle.addEventListener('click', _ => {
			if (stubToggle.classList.contains('active')) {
				stubToggle.classList.remove('active');
				input.value = '';
				input.disabled = false;
				target.innerHTML = '<li><em> bitte Suchbegriff eingeben </em></li>';
			} else {
				stubToggle.classList.add('active');
				input.value = 'keine Suche in Rumpfdatensätzen möglich';
				input.disabled = true;
				reworkToggle.classList.remove('active');
				target.innerHTML = stubs.map(r => r.rendered_link).join('');
			}
		})

		reworkToggle.addEventListener('click', _ => {
			if (reworkToggle.classList.contains('active')) {
				reworkToggle.classList.remove('active');
				input.value = '';
				input.disabled = false;
				target.innerHTML = '<li><em> bitte Suchbegriff eingeben </em></li>';
			} else {
				reworkToggle.classList.add('active');
				input.value = 'keine Suche in nachzubearbeitenden Datensätzen möglich';
				input.disabled = true;
				stubToggle.classList.remove('active');
				target.innerHTML = reworks.map(r => r.rendered_link).join('');
			}
		})
		
	}
}
