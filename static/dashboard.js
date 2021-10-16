var colors = {"0": "#e74c3c", "1": "#2ecc71"}

function raidProtection(token, data) {
	var request = new XMLHttpRequest()
	request.open("GET", `(website)/web/api/raid-protection/${token}/${data}`)
	request.send()
	request.onreadystatechange = (changeEvent) => {
		text = request.responseText
		if (text.includes("ratelimit")) {
			alert("You are being ratelimited!")
			return
		}
		var currentStatus = "Disabled"
		if (text == "1") {
			currentStatus = "Enabled"
		}
		var button = document.getElementById("raid-protection-button." + data)
		button.innerHTML = "Raid Protection: " + currentStatus
		button.style.background = colors[text]
	}
}

function toggleSnipe(token, data) {
	var request = new XMLHttpRequest()
	request.open("GET", `(website)/web/api/snipe/${token}/${data}`)
	request.send()
	request.onreadystatechange = (changeEvent) => {
		text = request.responseText
		if (text.includes("ratelimit")) {
			alert("You are being ratelimited!")
			return
		}
		var currentStatus = "Disabled"
		if (text == "1") {
			currentStatus = "Enabled"
		}
		var button = document.getElementById("snipe-button." + data)
		button.innerHTML = "Message Snipe: " + currentStatus
		button.style.background = colors[text]
	}
}

function toggleFilter(token, name, data) {
	var request = new XMLHttpRequest()
	request.open("GET", `(website)/web/api/filter/${token}/${name}/${data}`)
	request.send()
	request.onreadystatechange = (changeEvent) => {
		text = request.responseText
		if (text.includes("ratelimit")) {
			alert("You are being ratelimited!")
			return
		}
		var currentStatus = "Disabled"
		if (text == "1") {
			currentStatus = "Enabled"
		}
		var filterName = "Unknown"
		if (name == "insults") {
			filterName = "Insults"
		} else if (name == "spam") {
			filterName = "Spam"
		} else if (name == "links") {
			filterName = "Links"
		} else if (name == "mention") {
			filterName = "Mention"
		}
		var button = document.getElementById(`${name}-filter-button.${data}`)
		button.innerHTML = `${filterName}: ${currentStatus}`
	}
}

