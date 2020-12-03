import { Component } from 'react';

class GlobalState extends Component {

  constructor() {
    super();
    this.imageId = 0;
  }
  setImage(imageId) {
    this.imageId = imageId;
  }

  getImageId = () => {
    return this.imageId;
  }
}

export default GlobalState 

// set the user like sizeup is set
