using UnityEngine;


public class EarthData : MonoBehaviour, GetTheEarth
{
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    private Transform _earth;
    
    public Transform Earth {get => _earth ; set{ if(gameObject.name == value.gameObject.name) _earth = value;}}

    private void Awake()
    {
        _earth = transform;
        Earth = _earth;
    }
    
}
