const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value
const alertBox = document.getElementById('alert-box')


const handleAlerts = (type,msg) => {
    alertBox.innerHTML = `
    <div class="alert alert-${type}" role="alert">
        ${msg}
    </div>
    `
}


Dropzone.autoDiscover = false
const myDropzone = new Dropzone('#my-dropzone', {
    url: '/reports/upload/',
    init: function() {
        this.on('sending', function(file, xhr, formData){
            formData.append('csrfmiddlewaretoken', csrf)
        })
        this.on('success', function(file, response){
            const ex = response.ex
            if(ex){
                handleAlerts('danger', 'This file is already stored in the database')
            } else {
                handleAlerts('success', 'Successful upload!')
            }
        })
    },
    maxFiles: 3,
    maxFilessize: 3,
    acceptedFiles: '.csv',
})
