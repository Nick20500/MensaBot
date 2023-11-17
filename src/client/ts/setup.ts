//Eventlistener to first Button in Tab switch
const createAccountButton = document.getElementById('create-account-button');
createAccountButton?.addEventListener('click', createAccount);

//Eventlistener to second Button in Tab switch
const secondSetupButton = document.getElementById('mensas-and-menues-to-message-settings');
secondSetupButton?.addEventListener('click', () => switchFormTab('mensas-and-menues','message-settings'));

//Handle submit of Form
const submitButton = document.getElementById('set-message-settings');
submitButton?.addEventListener('click', submitForm);

async function createAccount(){
    const form = document.getElementById('create-account-form') as HTMLFormElement;
    const formData = new FormData(form);

    if(form.checkValidity()){
        let accountInfos = {} as {[key: string]: any};
        for (const [key, value] of formData){
            accountInfos[key] = value;
        }

        const response = await fetch('/create-account', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(accountInfos)
        });

        if(response.ok){
            //TODO: if phone number already exists, prompt that & refer to account tab to edit message settings

            //Account is new and got created successfull, continue with message set-up
            switchFormTab('create-account','mensas-and-menues');
        } else {
            //TODO: if error prompt that & let user try account creation again
        }
    }
}

function switchFormTab(oldDivId: string, newDivId: string){
    const oldFormPart = document.getElementById(oldDivId + '-form-part');
    oldFormPart?.classList.remove('activeFormPart');

    const newFormPart = document.getElementById(newDivId + '-form-part');
    newFormPart?.classList.add('activeFormPart');

    const oldTab = document.getElementById(oldDivId + '-tab');
    oldTab?.classList.remove('activeTab');

    const newTab = document.getElementById(newDivId + '-tab');
    newTab?.classList.add('activeTab');
}

async function submitForm(){
    //Get choosen Mensas    
    const selectedMensaCheckboxes = document.querySelectorAll("#mensas-and-menues-form-part input[type='checkbox']:checked");
    let selectedMensas = [] as string[];
    for (const mensa of selectedMensaCheckboxes){
        selectedMensas.push(mensa.id);
    }

    //Get choosen Days for schedule
    const selectedDaysCheckboxes = document.querySelectorAll("#schedule-form-part input[type='checkbox']:checked");
    let selectedDays = [] as string[];
    for (const day of selectedDaysCheckboxes){
        selectedDays.push(day.id);
    }

    //Get choosen time for schedule
    const selectedTime = document.getElementById('time') as HTMLInputElement;

    //set the body for the POST request
    const body = {
        mensas: selectedMensas,
        days: selectedDays,
        time: selectedTime.value,
    }

    const response = await fetch('/message-setup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }, 
        body: JSON.stringify(body)
    });

    if(response.ok){
        //TODO: display new page where it says 'mensabot setup was successfull' & short summary of the choosen settings & if the user wants changes, it can do them in the user tab
        const lastFormPart = document.getElementById('message-settings-form-part');
        lastFormPart?.classList.remove('activeFormPart');

        const successPage = document.getElementById('successful-setup-page');
        if(successPage){
            successPage.style.display = 'flex';
        }

        console.log('setting transmission to backend was GOOOD');
    } else {
        //TODO: display error message & that user should try setup again
        console.log('Error: ' + response.status + ' - ' + response.statusText);
    }
}