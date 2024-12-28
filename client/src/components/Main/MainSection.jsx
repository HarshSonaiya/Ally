import React from 'react'
import './mainSection.css'
import { assets } from '../../assets/assets'

const Main = () => {
    return (
        <div className='main'>
            <div className="nav">
                <p>Navio</p>
            </div>
            <div className="main-container">
                <div className="greet">
                    <p><span>Hey there!</span></p>
                    <p>What can I do to assist you?</p>
                </div>
                <div className="cards">
                    <div className="card">
                        <p>Summarize a concept</p>
                    </div>
                    <div className="card">
                        <p>Tell me some international news.</p>
                    </div>
                    <div className="card">
                        <p>{"Know about the latest happenings in the Tech. Industry."}</p>
                    </div>
                    <div className="card">
                        <p>Want to learn a about a new technology.</p>
                    </div>
                </div>
                <div className="main-bottom">
                    <div className="search-box">
                        <input type="text" placeholder='What do you want to ask?' />
                        <div>
                            <img src={assets.gallery_icon} alt="" />
                            <img src={assets.web_icon} alt="" />
                            <img src={assets.send_icon} alt="" />
                        </div>
                    </div>
                    <p className='bottom-info'>
                        {"Note that the information provided by Navio may not always be fully accurate. We recommend verifying any details independently to ensure correctness."}
                    </p>
                </div>
            </div>
        </div>

    )
}

export default Main