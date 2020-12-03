import React, { Component } from 'react';
import Answers from './Answers';

class Leaderboard extends Component {
	
	constructor(props){
		super();
		this.state = {
      mostCommented : '',
			imagePath : '',
    }
	}
	
  componentDidMount() {
	  // get the most commented on picture
      fetch(this.props.DATA_URI + "/get_image?selected_image=most_answers", {
		    method: 'GET',
		    headers: { 'Accept': 'application/json' },
		    credentials: 'same-origin',
	   })
	   .then((response) => response.json())
	   .then((data) => {
		   this.setState( { 
				mostCommented : data.image_id,
				imagePath : data.imagePath 
				} );
	   })
	   .catch((error) => {
		   console.log("error is ", error);
	   });
  }
	  
  render() {
	return(
		<div>
		{this.state.mostCommented}
		<img src={this.props.DATA_URI + this.state.imagePath} alt="what is it img" />
		Here is the leaderboard!
    <br />
    Now I should be able to get an answer component down here with the right
    answers
    { this.state.mostCommented ? <Answers imageId={this.state.mostCommented} DATA_URI={this.props.DATA_URI} trigger={this.state.trigger} unTriggerAnswers={this.unTriggerAnswers} triggerAnswers={this.triggerAnswers} user={this.props.user} } answerToggle={this.props.answerToggle} /> : null }
	</div>
	);
    }
}

export default Leaderboard
