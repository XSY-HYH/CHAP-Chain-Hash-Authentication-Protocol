## FAQ - Please Read Before Opening an Issue

### Q: Why not use TLS/HTTPS?
A: Because my use case is frontend pages, which can't handle TLS. Certificate management is also a burden.

### Q: Where's the code?
A: Protocol documentation comes first. For implementation, refer to the original project [Repository-File-Server](https://github.com/XSY-HYH/Repository/blob/main/Services/ChapAuthService.cs). Contributions are welcome.

### Q: Is the name a ripoff?
A: CHAP = Chain Hash Authentication Protocol. Just a coincidence. You can also call it the ZIM protocol.

### Q: Rolling your own protocol?
A: Yes, I was bored. But AES is a standard algorithm — no new encryption was invented.

### Q: No formal verification?
A: You're right. Pull requests or donations to fund an audit are welcome.

### Q: The server is stateful and can't be distributed?
A: This isn't designed for Google. It's for frontend, low-performance, or embedded use cases that still need secure sessions.

### Q: What about DoS protection?
A: Do you think TLS protects against SYN flood?

### Q: Your thing doesn’t have that elliptic curve stuff or whatever. Is it even secure?
A: Engineering is about solving problems, not adding more of them.
If a complex implementation isn’t as effective as a simple one, why would I use the complex one? That’s it. If a simple approach works better than a complicated one, why would I choose complexity? Besides, if you want to reuse it, you’d have to learn all these algorithms first—aren’t you tired of that? You go through all that trouble and make such a big scene, isn’t it just because the users don’t understand it and that makes them feel secure? But in reality, users need to understand it in order to implement it themselves. If you make it so people can’t understand it, they won’t know what’s wrong when something breaks, and the more complex it is, the more likely things go wrong—there’s no way you don’t know that.
