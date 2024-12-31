import React, { useState } from 'react';
import Button from '../../components/ui/Button';
import { assets } from '../../assets/assets';
import './LandingPage.css';
import Hamburger from '../icons/HamBurger';

const Index = () => {

  const [menuOpen, setMenuOpen] = useState(false);

  const toggleMenu = () => {
    setMenuOpen(prevState => !prevState);
  };

  const displayCode = `const ally = new AllyAI({
  apiKey: 'your-api-key'
});

const response = await ally.analyze({
  text: documentContent,
  type: 'document'
});`;

  const handleGoogleLogin = () => {
    const loginUrl = "http://localhost:8000/auth/google-auth";
    window.location.href = loginUrl; 
  };

  return (
    <div className="landing-page">
      {/* Header Section */}
      <header>
        <div className="logo">
          {/* <h1>Ally.</h1> */}
          <img src={assets.logo} alt="logo" />
        </div>
        <nav>
          <ul>
            <li><a href="#features">Features</a></li>
            <li><a href="#pricing">Pricing</a></li>
            <li><a href="#docs">Documentation</a></li>
            <li><a href="#developer">Developer Portal</a></li>
          </ul>
          <div className="auth-buttons">
            <Button size='sm' onClick={handleGoogleLogin}>Sign In</Button>
            {/* <Button size='sm'>Sign Up</Button> */}
          </div>
        </nav>
        <Button variant="outline" className="menu-toggle" size="sm" onClick={() => toggleMenu()}>
          <Hamburger isOpen={menuOpen} />
          {/* Hello */}
        </Button>
      </header>

      {/* Hero Section */}
      <section className="hero">
        <div className='hero-left'>
          <h1>Your Ally for Every Conversation, Insight, and Idea.</h1>
          <p>Experience the future of conversation with Ally, your AI companion that understands documents, transcribes media, and searches the web — all in one place.</p>
          <div className="cta-buttons">
            <Button size="lg">Start Chatting</Button>
            <Button variant="outline" size="lg">Try Demo</Button>
          </div>
        </div>
        <div className='hero-right'>
          <img src={assets.right_section} alt="Ally." />
        </div>
      </section>

      {/* Features Section */}
      <section className="features" id="features">
        <h2>Powerful Features for Every Need</h2>
        <div className="features-grid">
          {features.map((feature, index) => (
            <div className="feature-card" key={index}>
              <div className="feature-icon">{feature.icon}</div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Interactive Demo Section */}
      <section className="demo">
        <h2>Try Ally Now</h2>
        <div className="chat-interface">
          <div className="chat-message ai">
            <img src={assets.ally_icon} alt="ally_icon" />
            <p>Hello! How can I assist you today?</p>
          </div>
          <div className="chat-message user">
            <p>Can you help me analyze this document?</p>
            <img src={assets.user} alt="user" />
          </div>
          <div className="chat-message ai">
            <img src={assets.ally_icon} alt="ally_icon" />
            <p>{`Of course! Please share your document, and I'll analyze it for you.`}</p>
          </div>
        </div>
      </section>

      {/* Developer Tools Section */}
      <section className="developer-tools" id="developer">
        <div className="content">
          <h2>Customize Your Experience</h2>
          <p>Build powerful AI-driven applications with our developer-friendly tools and APIs.</p>
          <Button size='sm'>Access Developer Portal</Button>
        </div>
        <div className="code-preview">
          <pre>
            <code>{displayCode}
            </code>
          </pre>
        </div>
      </section>

      {/* Trusted By Section */}
      <section className="trusted-by">
        <h2>Trusted by Industry Leaders</h2>
        <div className="company-logos">
          <div className="logo">Company 1</div>
          <div className="logo">Company 2</div>
          <div className="logo">Company 3</div>
          <div className="logo">Company 4</div>
        </div>
      </section>

      {/* Footer Section */}
      <footer>
        <div className="footer-content">
          <div className="footer-brand">
            <h2>Ally.</h2>
            <p>Your AI companion for smarter conversations and insights.</p>
          </div>
          <div className="footer-links">
            <div className="link-column">
              <h3>Products</h3>
              <ul>
                <li><a href="#features">Features</a></li>
                <li><a href="#pricing">Pricing</a></li>
                <li><a href="#enterprise">Enterprise</a></li>
              </ul>
            </div>
            <div className="link-column">
              <h3>Company</h3>
              <ul>
                <li><a href="#about">About</a></li>
                <li><a href="#careers">Careers</a></li>
                <li><a href="#contact">Contact</a></li>
              </ul>
            </div>
            <div className="link-column">
              <h3>Legal</h3>
              <ul>
                <li><a href="#privacy">Privacy</a></li>
                <li><a href="#terms">Terms</a></li>
                <li><a href="#security">Security</a></li>
              </ul>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

const features = [
  {
    icon: "📄",
    title: "Document Analysis",
    description: "Upload PDFs and get instant insights. Ally reads and understands your documents, making information retrieval effortless."
  },
  {
    icon: "🎙️",
    title: "Media Transcription",
    description: "Convert audio and video files into accurate transcripts with AI-powered transcription technology."
  },
  {
    icon: "📝",
    title: "Custom Summaries",
    description: "Generate precise summaries for specific segments of your media files, saving time and increasing productivity."
  },
  {
    icon: "🔍",
    title: "Web Search",
    description: "Access real-time information from the web to enhance your conversations with up - to - date knowledge."
  },
  {
    icon: "🛠️",
    title: "Developer Playground",
    description: "Customize chunking strategies and LLM parameters in our developer-friendly environment."
  },
  {
    icon: "🤖",
    title: "AI Assistant",
    description: "Experience natural conversations with our advanced AI that learns and adapts to your needs."
  }
];

export default Index;