
const form = document.getElementById('form')

const add = document.getElementById('form-add')
const removes = form.querySelectorAll('.form-remove')

const form_list = document.getElementById('form-list')

const token = document.getElementById('csrf_token')

let length = form_list.children.length

add.addEventListener('click', e => {
	const prefix = `perm-list-${length++}-`

	const item = document.createElement('p')

	const input = document.createElement('input')
	input.type = 'text'
	input.name = prefix + 'userid'
	input.id = prefix + 'userid'

	const select = document.createElement('select')
	select.classList.add('send-perms', 'button')
	select.name = prefix + 'perms'
	select.id = prefix + 'perms'

	const options = ['none', 'view', 'post', 'edit', 'owner']
	for (const tt of options) {
		const option = document.createElement('option')
		option.value = tt
		option.textContent = tt
		if (tt == 'edit') option.selected = 'true'
		select.append(option)
	}

	const a = document.createElement('a')
	const button = document.createElement('button')
	button.type = 'button'
	button.classList.add('button', 'form-remove')
	button.textContent = '-'
	button.addEventListener('click', e => {
		form_list.remove(item)
	})
	a.append(button)

	item.append(input, ' ', select, ' ', a)

	form_list.append(item)
})

for (const remove of removes) {
	remove.addEventListener('click', e => {
		form_list.remove(remove.parentElement)
	})
}

