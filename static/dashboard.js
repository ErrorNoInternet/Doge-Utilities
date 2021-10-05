function raidProtection(token, data) {
	var request = new XMLHttpRequest()
	request.open("GET", `(website)/web/api/raid-protection/${token}/${data}`)
	request.send()
	request.onreadystatechange = (changeEvent) => {
		text = request.responseText
		var currentStatus = "Enabled"
		if (text == "0") {
			currentStatus = "Disabled"
		}
		var button = document.getElementById("raid-protection-button." + data)
		button.innerHTML = "Raid Protection: " + currentStatus
	}
}
