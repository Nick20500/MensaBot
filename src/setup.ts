function switchFormTab(oldDivId: string, newDivId: string){
    const oldTab = document.getElementById(oldDivId);
    oldTab?.classList.remove("activeTab");

    const newTab = document.getElementById(newDivId);
    newTab?.classList.add("activeTab");
}