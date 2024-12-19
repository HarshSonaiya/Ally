import React from 'react'
import './Main.css'
import { assets } from '../../assets/assets'

const Main = () => {
    return (
        <div className='main'>
            <div className="nav">
                <p>Navio</p>
            </div>
            <div className="main-container">
                <div className="greet">
                    <p><span>Hello matey,</span></p>
                    <p>What can I hep with ?</p>
                </div>
                <div className="cards">
                    <div className="card">
                        <p>Summarize a concept</p>
                    </div>
                    <div className="card">
                        <p>Tell me some international news.</p>
                    </div>
                    <div className="card">
                        <p>Know about the latest happenings in the Tech. Industry.</p>
                    </div>
                    <div className="card">
                        <p>Want to learn a about a new technology.</p>
                    </div>
                </div>
                <div className="main-bottom">
                    <div className="search-box">
                        <input type="text" placeholder='What do you want to ask?'/>
                        <div>
                            <img src={assets.gallery_icon} alt="" />
                            <img src={assets.web_icon} alt="" />
                            <img src={assets.send_icon} alt="" />
                        </div>
                    </div>
                    <p className='bottom-info'>
                        Navio may display inaccurate information. Please perform your due diligence afterwards.
                    </p>
                </div>
            </div>
        </div>

    )
}

export default Main