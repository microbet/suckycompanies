class Company {

  constructor() {
    this.name = '';
    this.flaskMessage = '';
  }

  requestCompany(selectedCompany, server, companyId=null, userId=null, sessionvalue=null) {
    var promise = fetch( server + '/get_company?companyId=' + companyId
       + "&selected_company=" + selectedCompany + "&user_id=" 
       + userId + "&sessionvalue=" + sessionvalue, {
      credentials : 'same-origin',
      method: 'GET',
      headers: { 'Accept': 'application/json', },
	})
	.then(response => response.json())
         .then(data =>  {
             this.name = data.name;
             this.companyId = data.company_id;
         })
         .catch(error => {
           this.setState({ error, isLoading: false});
           console.log("error: ", error);
        });
    return promise;
  }

   setCompanyId(companyId) {
    this.companyId = companyId;
  }

}

export default Company 
