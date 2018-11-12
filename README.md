# Typed Asana API

Type Python Objects to complement [python-asana](https://github.com/Asana/python-asana)

## Inspiration

In a age of IDEs with code completion, I found python-asana lacking in their implementation of data structures regarding the api.
This module is a WIP and does not implement all known objects as of yet.

Implemented API Objects:  
- [ ]  Attachments  
- [ ]  Custom Field Settings  
- [ ]  Custom Fields  
- [ ]  Event  
- [ ]  Organization Export  
- [ ]  Project Membership  
- [x]  Project Statue  
- [x]  Project  
- [ ]  Section  
- [ ]  Story  
- [x]  Tag  
- [x]  Task  
- [ ]  Teams  
- [x]  User  
- [ ]  Webhook  
- [x]  WorkSpace  

## Acknowledgements
Thanks to the creators over at [quicktype](https://app.quicktype.io/) I was able to save some time from having to type for each object or make a custom generator that uses Asana's API Meta Data.
Their API Meta Data doesn't cover all types for list, hence why i went this route. 