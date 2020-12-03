import React, { Component } from 'react';

class Register extends Component {

  constructor(props) {
    super();
    this.state = {
      username: '',
      password: '',
    }
  }

  handleUnameChange = event => {
    this.setState( { username: event.target.value } );
  }

  handlePwordChange = event => {
    this.setState( { password: event.target.value } );
  }

  handleRegister = () => {

    const fd = new FormData();
    fd.append('username', this.state.username);
    fd.append('password', this.state.password);
    fetch( this.props.DATA_URI + '/register', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
      },
      body: fd
    })
    .then((response) => response.json())
    .then((data) => {
      console.log("data = ", data);
    })
    .catch((error) => {
      console.log("error ", error);
    });
  }

  render() {

    return(
      <span className="Small-form">
      <form onSubmit={this.handleRegister}>
      Username: <input type="text" onChange={this.handleUnameChange}/>
      Password: <input type="text" onChange={this.handlePwordChange}/>
      <input type="submit" value="register" />
      </form>
       <button onClick={(show) => this.props.switchForm('login')}  styles="display: inline" className="Text-button"><font size="1">Need to log in?</font></button>
      </span>
    );
  }
}

export default Register 
