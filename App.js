import axios from 'axios';
import React, { Component } from 'react';
import { View } from 'react-native';
import { GiftedChat } from 'react-native-gifted-chat';


const BOT = {
  _id: 2,
  name: 'Man',
  avatar: ''
}

 

export default class App extends Component {

   
  constructor(props) {
    super(props);
    this.state = {
      messages: [{_id:1, text: 'Hello', createdAt: new Date(),
                  user: BOT}],
      id: 1,
      name: '',
      values: [{}],
      text: ''
    };

  this.onSend = this.onSend.bind(this);
  // this.onQuickReply = this.onQuickReply.bind(this);
  this.SendBotResponse = this.SendBotResponse.bind(this);
    
}

  
onSend = async (messages = [])=>{


this.setState((previousState) => ({

messages: GiftedChat.append(previousState.messages, messages)


}));

let message = messages[0].text 
await axios.get(`http://10.0.2.2:5000/get?msg=${message}`).then((response) => {
  this.SendBotResponse(response.data);}).catch((error) => {
  // handle error
  console.log(error);
})

}

SendBotResponse = (text)=> {
  
  if(typeof text=='string')
  {this.setState({text: text})
  let msg = 
    {
    _id: this.state.messages.length + 1,
    text: this.state.text , createdAt: new Date(),
    user: BOT
  }
  this.setState((previousState)=>({
    messages: GiftedChat.append(previousState.messages, [msg]),
 }));

}
else{
  this.setState({values:text})
  let msg = {
    _id: this.state.messages.length + 1,
      text: 'Please select suitable input:',
      createdAt: new Date().getTime(),
      user: BOT,
      quickReplies:{
        type:'checkbox',
        values: this.state.values,
      },
  
    }
    this.setState((previousState)=>({
      messages: GiftedChat.append(previousState.messages, [msg]),
   }));
  
}
}

onQuickReply = async (quickReply) => {
  this.setState((previouseState) => ({
    messages: GiftedChat.append(previouseState.messages, quickReply),
  }));
  var message = [];
  for (var index = 0; index < quickReply.length; index++) {
    message.push(quickReply[index].value);
  }
  
  await axios.get(`http://10.0.2.2:5000/get?msg=${message}`).then((response) => {
  this.SendBotResponse(response.data);}).catch((error) => {
  // handle error
  console.log(error);
})

}


  render() {
    return (
      <View style={{flex:1, backgroundColor:'white'}}>
        <GiftedChat messages={this.state.messages}
        onSend={(messages)=>this.onSend(messages)}
        onQuickReply={(quickReply) => this.onQuickReply(quickReply)}
        user={{_id: 1}}
        />
      </View>
    )
  }
}